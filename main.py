import warnings
warnings.filterwarnings(action="ignore")

import telebot

from packages import db_manager
from packages.networks import *
import config

bot = telebot.TeleBot(config.TOKEN)

markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
help_button = telebot.types.KeyboardButton("Help")
report_button = telebot.types.KeyboardButton("Github")
markup.add(help_button, report_button)

survey_kb = telebot.types.InlineKeyboardMarkup()
yes_button = telebot.types.InlineKeyboardButton(text="Yes", callback_data="Yes")
no_button = telebot.types.InlineKeyboardButton(text="No", callback_data="No")
survey_kb.add(yes_button, no_button)

hello_sticker = open('stickers/hello.webp', 'rb')
work_sticker = open('stickers/work.webp', 'rb')
done_sticker = open('stickers/done.webp', 'rb')
error_sticker = open('stickers/error.webp', 'rb')

# load all neural networks
qa_pipline = pipeline(task='question-answering',
                        model='bert-large-uncased-whole-word-masking-finetuned-squad',
                        tokenizer='bert-large-uncased-whole-word-masking-finetuned-squad')

model = SentenceTransformer('cross-encoder/qnli-electra-base')

kw_model = KeyBERT()

db_manager.create_db() # create db if not exists


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_sticker(message.chat.id, hello_sticker)
    bot.send_message(message.chat.id, 'Hi, my name is wiki_assistant_bot and I\'ll answer your questions!', reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def inline(callback):
    satisfied = None
    
    if callback.data == "Yes":
        satisfied = True
    if callback.data == "No":
        satisfied = False

    if satisfied is not None:
        db_manager.update_satisfied(callback.message.chat.id, satisfied)
        bot.send_message(callback.message.chat.id, "Thank you, It was noted on your last question!")


@bot.message_handler(content_types=['text'])
def text_handler(message):
    if message.text == "Help":
        bot.send_message(message.chat.id, "<help>")
    
    elif message.text == "Github":
        bot.send_message(message.chat.id, "https://github.com/EskimoCold/wiki_assistant")

    else:
        question = message.text

        bot.send_sticker(message.chat.id, work_sticker)

        print(f"question from {message.chat.id}: {question}")

        try:
            answer, url = question_to_answer(question, qa_pipline, model, kw_model)

            db_manager.save_q_and_a(question, answer, message.chat.id)

            print(f"answer on {message.chat.id}:{answer}")
            print(f"url on {message.chat.id}:{url}")

            if answer is None:
                bot.send_sticker(message.chat.id, error_sticker)
                bot.send_message(message.chat.id, "Sorry, I can\'t answer your question(")
            else:
                bot.send_sticker(message.chat.id, done_sticker)
                bot.send_message(message.chat.id, f"{answer}\n\nHere you can read all information: {url}")
                bot.send_message(message.chat.id, "Are you satisfied with the answer?", reply_markup=survey_kb)
        except:
            bot.send_sticker(message.chat.id, error_sticker)
            bot.send_message(message.chat.id, "Sorry, I can\'t answer your question(")


if __name__ == "__main__":
    print('bot started!')
    bot.polling(non_stop=config.NONE_STOP)