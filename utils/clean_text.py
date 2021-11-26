from bs4 import BeautifulSoup
import re

def remove_html(post_text):
    return BeautifulSoup(post_text, "html.parser").text

def remove_between_square_brackets(post_text):
    return re.sub('\[[^]]*\]', '', post_text)

def remove_post_id(post_text):
    return post_text.split("post_id: ", 1)[0]

def remove_backslash_symbols(post_text):
    return post_text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ').strip()


