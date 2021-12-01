# module for text preprocessing
from bs4 import BeautifulSoup
import re
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

def remove_html(post_text):
    """remove html text from raw post content"""
    return BeautifulSoup(post_text, "html.parser").text

def remove_between_square_brackets(post_text):
    """remove text between square brackets from raw post content"""
    return re.sub('\[[^]]*\]', '', post_text)

def remove_post_id(post_text):
    """remove post id at the end of raw post content"""
    return post_text.split("post_id: ", 1)[0]

def remove_backslash_symbols(post_text):
    """remove special symbols from raw post content"""
    return post_text.replace('\r\n\r\n', ' ') \
        .replace('\n', ' ').replace('\r', ' ') \
        .replace('\t', ' ').replace('\xa0', ' ').strip()

def remove_links(post_text):
    """remove links from raw post content"""
    return re.sub(r"http\S+", '', post_text)

def lemmatize(post_text):
    """lemmatize raw post content"""
    return ' '.join([lemmatizer.lemmatize(w) for w in word_tokenize(post_text)])

def preprocess_topic(posts_content):
    """apply all preprocessing steps to each raw post content"""
    preprocess_pipeline = [
                           remove_html, remove_between_square_brackets, remove_post_id,
                           remove_backslash_symbols, remove_links, lemmatize
                           ]

    for step in preprocess_pipeline:
        posts_content = map(step, posts_content)

    return list(posts_content)

def preprocess_keywords(posts_content):
    """apply all preprocessing steps to each raw post content"""
    preprocess_pipeline = [
                           remove_html, remove_between_square_brackets, remove_post_id,
                           remove_backslash_symbols, remove_links
                           ]

    for step in preprocess_pipeline:
        posts_content = map(step, posts_content)

    return list(posts_content)




