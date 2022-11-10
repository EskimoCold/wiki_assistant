import os

from scipy.spatial.distance import cosine
import numpy as np
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from keybert import KeyBERT

from packages import parsers
from packages import preprocessing


def load_all_neuralnetworks():
    qa_pipline = pipeline(task='question-answering',
                            model='bert-large-uncased-whole-word-masking-finetuned-squad',
                            tokenizer='bert-large-uncased-whole-word-masking-finetuned-squad')

    sentence_model = SentenceTransformer('cross-encoder/qnli-electra-base')

    kw_model = KeyBERT()
    
    return qa_pipline, sentence_model, kw_model


def keywords_from_question(model, question:str, minkw:int=1, maxkw:int=3) -> list:
    return model.extract_keywords(question, keyphrase_ngram_range=(minkw, maxkw), stop_words=None)[0][0]


def get_answer_from_text(qa_pipeline, question:str, context:str) -> str:
    prediction = qa_pipeline({
        "context" : context,
        "question" : question
    })

    return prediction['answer']


def get_most_similar_part(model, query:str, sentences:list) -> str:
    query_embed = model.encode([query])
    corpus_embed = model.encode(sentences)

    similarities = []

    for embedding in corpus_embed:
        similarities.append(1 - cosine(query_embed, embedding))

    similarities = np.array(similarities)

    best_index = np.argmax(similarities)
    best_part = sentences[best_index]
    
    return best_part, best_index


def question_to_answer(question:str, qa_pipline, model, kw_model, minkwlen:int=0):
    question_preprocessed = preprocessing.question_preprocessing(question)

    parsed = []
    keyw = []
    for i in range(minkwlen, len(question_preprocessed)):
        try:
            keywords = keywords_from_question(kw_model, question, len(question.split()) - i - 1, len(question.split()) - i)
            keyw.append(keywords)
            p = parsers.parse_wiki(keywords)
            if p is not None:
                parsed.append(p)
        except:
            continue
    
    p = parsers.parse_wiki(question_preprocessed)
    if p is not None:
        parsed.append(p)
    
    if len(parsed) == 0:
        return None

    parsed = list(set(parsed))
    
    print(f"parsed, keywords: {keyw}")

    preprocessed = []
    for i in range(len(parsed)):
        preprocessed.append(' '.join(preprocessing.text_preprocessing(parsed[i][0])))

    print(f"preprocessed...")
    best_part, best_index = get_most_similar_part(model, question_preprocessed, preprocessed)
    best_url = parsed[best_index][1]
    print("best part selected...")
    answer = get_answer_from_text(qa_pipline, question, best_part)

    return answer, best_url


def get_large_audio_transcription(path:str) -> str:
    r = sr.Recognizer()
    sound = AudioSegment.from_ogg(path)  
    
    chunks = split_on_silence(sound,
        min_silence_len = 500,
        silence_thresh = sound.dBFS-14,
        keep_silence=500,
    )
    
    folder_name = "audio-chunks"
    
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
        
    whole_text = ""
    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
        audio_chunk.export(chunk_filename, format="wav")
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            try:
                text = r.recognize_google(audio_listened)
                
            except sr.UnknownValueError as e:
                return 0
            
            else:
                text = f"{text.capitalize()}. "
                whole_text += text
                
    return whole_text
