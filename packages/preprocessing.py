from bs4 import BeautifulSoup
import spacy


nlp = spacy.load('en_core_web_lg')

def strip_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    stripped_text = soup.get_text(separator=" ")
    return stripped_text


def remove_whitespace(text):
    text = text.strip()
    return " ".join(text.split())


def text_preprocessing(text):
    text = strip_html_tags(text)
    text = remove_whitespace(text)
    text = text.lower()

    doc = nlp(text)

    clean_text = []
    
    for token in doc:
        flag = True
        edit = token.text
        if token.pos_ == 'SYM' and flag == True: 
            flag = False
        if edit != "" and flag == True:
            clean_text.append(edit) 

    return clean_text


def question_preprocessing(text):
    doc = nlp(text)

    clean_text = []
    
    for token in doc:
        flag = True
        edit = token.text

        if token.pos_ == 'PUNCT' and flag == True: 
            flag = False

        if edit != "" and flag == True:
            clean_text.append(edit) 
       
    return clean_text