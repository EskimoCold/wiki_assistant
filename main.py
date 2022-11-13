from time import time
import warnings
warnings.filterwarnings(action="ignore")

import telebot
import argparse

from packages import db_manager, messages
from packages.networks import *
import config

# argparsing
argparser = argparse.ArgumentParser(description='Wiki assistant')
argparser.add_argument("--token", type=str, default=config.TOKEN)
args = argparser.parse_args()
TOKEN = args.token

bot = telebot.TeleBot(TOKEN)

# setuping keyboards
markup = telebot.types.ReplyKeyboardMarkup(row_width=1)
help_button = telebot.types.KeyboardButton("Help")
report_button = telebot.types.KeyboardButton("Github")
markup.add(help_button, report_button)

survey_kb = telebot.types.InlineKeyboardMarkup()
yes_button = telebot.types.InlineKeyboardButton(text="Yes", callback_data="Yes")
no_button = telebot.types.InlineKeyboardButton(text="No", callback_data="No")
survey_kb.add(yes_button, no_button)

# loading nn + creating database
qa_pipline, sentence_model, kw_model = load_all_neuralnetworks()
db_manager.create_db()

if not os.path.exists("voice_msgs"):
    os.mkdir("voice_msgs")


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAOkY26AqvRhVAf-GJmh5f-zqa64tkcAAm83AALpVQUYRePim7upqHQrBA")
    bot.send_message(message.chat.id, messages.bot_messages["greeting"], reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def inline(callback):
    satisfied = None
    
    if callback.data == "Yes":
        satisfied = True
    if callback.data == "No":
        satisfied = False

    if satisfied is not None:
        db_manager.update_satisfied(callback.message.chat.id, satisfied)
        bot.send_message(callback.message.chat.id, messages.bot_messages["callback"])


@bot.message_handler(content_types=['text'])
def text_handler(message):
    if message.text == "Help":
        bot.send_message(message.chat.id, messages.bot_messages["help"])
    
    elif message.text == "Github":
        bot.send_message(message.chat.id, messages.bot_messages["github"])

    else:
        try:
            question = message.text

            bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAOiY26AgW2FjyArKkq9OwU2uqjymSYAAoI3AALpVQUYL-ts6UKMyeorBA")

            print(f"question from {message.chat.id}: {question}")

            try:
                answer, url = question_to_answer(question, qa_pipline, sentence_model, kw_model)

                db_manager.save_q_and_a(question, answer, message.chat.id)

                print(f"answer on {message.chat.id}:{answer}")
                print(f"url on {message.chat.id}:{url}")

                if answer is None:
                    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAOgY26AS3xKGGUa4Gc8hW_W7aRgfQ4AAnA3AALpVQUYH28VcdzDf3MrBA")
                    bot.send_message(message.chat.id, messages.bot_messages["error"])
                    
                else:
                    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAOeY25_oN1YabWRusm36lpROykLMyIAAow3AALpVQUYI0cmZPnyzQ8rBA")
                    bot.send_message(message.chat.id, f"{answer}\n\nHere you can read all information: {url}")
                    bot.send_message(message.chat.id, messages.bot_messages["survey"], reply_markup=survey_kb)
                    
            except:
                bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAOgY26AS3xKGGUa4Gc8hW_W7aRgfQ4AAnA3AALpVQUYH28VcdzDf3MrBA")
                bot.send_message(message.chat.id, messages.bot_messages["error"])
                
        except:
            pass


@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    with open(f'voice_msgs/{message.chat.id}_{int(time())}.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)
        
    name = f'voice_msgs/{message.chat.id}_{int(time())}.ogg'
    transcription = get_large_audio_transcription(name)
    
    if transcription == 0:
        bot.send_message(message.chat.id, messages.bot_messages["not_recognized"])
        
    else:
        question = transcription[:-2]+'?'
        bot.send_message(message.chat.id, f'Your voice was recognized as: {question}')
        
        try:
            bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAOiY26AgW2FjyArKkq9OwU2uqjymSYAAoI3AALpVQUYL-ts6UKMyeorBA")

            print(f"question from {message.chat.id}: {question}")

            try:
                answer, url = question_to_answer(question, qa_pipline, sentence_model, kw_model)

                db_manager.save_q_and_a(question, answer, message.chat.id)

                print(f"answer on {message.chat.id}:{answer}")
                print(f"url on {message.chat.id}:{url}")

                if answer is None:
                    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAOgY26AS3xKGGUa4Gc8hW_W7aRgfQ4AAnA3AALpVQUYH28VcdzDf3MrBA")
                    bot.send_message(message.chat.id, messages.bot_messages["error"])
                    
                else:
                    bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAOeY25_oN1YabWRusm36lpROykLMyIAAow3AALpVQUYI0cmZPnyzQ8rBA")
                    bot.send_message(message.chat.id, f"{answer}\n\nHere you can read all information: {url}")
                    bot.send_message(message.chat.id, messages.bot_messages["survey"], reply_markup=survey_kb)
                    
            except:
                bot.send_sticker(message.chat.id, "CAACAgIAAxkBAAOgY26AS3xKGGUa4Gc8hW_W7aRgfQ4AAnA3AALpVQUYH28VcdzDf3MrBA")
                bot.send_message(message.chat.id, messages.bot_messages["error"])
                
        except:
            pass        


if __name__ == "__main__":
    print('bot started!')
    bot.polling(non_stop=config.NONE_STOP)
