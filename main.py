# import os, shutil
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np

import tqdm
tqdm.tqdm.pandas()

import ast
import logging
from flask import Flask, request, render_template, flash, redirect, jsonify
from flask_cors import CORS
# from werkzeug.utils import secure_filename

from utils.clean_text import remove_html, remove_between_square_brackets, remove_post_id, remove_backslash_symbols
from configs.api import api_config

# keyword extraction
from keybert import KeyBERT
kw_extraction_model = KeyBERT()

# topic extraction
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer

class LemmaTokenizer:
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

vectorizer_model= CountVectorizer(tokenizer=LemmaTokenizer(), ngram_range=(1, 3), stop_words="english")

topic_model = BERTopic(vectorizer_model=vectorizer_model)
topic_model = topic_model.load('models_artifact/berttopic_model_lemmatized.bt')


PORT = api_config['port']
# UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
cors = CORS(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024 * 1024 * 1024

@app.route('/', methods=['GET', 'POST'])
def ping():
    return 'pong'

@app.route('/api/autokeyword', methods=['GET'])
def keyword_extractor():
    try:
        # Get data
        keywords_number = ast.literal_eval(request.args.get('keywords_number'))
        post_id = ast.literal_eval(request.args.get('post_ids'))
        posts_content = ast.literal_eval(request.args.get('posts_content'))

        # Clean post content
        posts_content = map(remove_html, posts_content)
        posts_content = map(remove_between_square_brackets, posts_content)
        posts_content = map(remove_post_id, posts_content)
        posts_content = map(remove_backslash_symbols, posts_content)
        posts_content = list(posts_content)

        # extract keywords
        result = []
        if keywords_number < 1:
            for post_content in posts_content:
                keywords = kw_extraction_model.extract_keywords(post_content, keyphrase_ngram_range=(1, 3),
                                                     stop_words='english', use_mmr=True, diversity=0.5,
                                                     top_n=20)
                filtered_keywords = list(filter(lambda x: x[1] > keywords_number, keywords))
                if len(filtered_keywords) == 0:
                    result.append([np.NaN])
                else:
                    result.append(list(map(lambda x: x[0], filtered_keywords)))

        else:
            for post_content in posts_content:
                keywords = kw_extraction_model.extract_keywords(post_content, keyphrase_ngram_range=(1, 3),
                                                     stop_words='english', use_mmr=True, diversity=0.5,
                                                     top_n=keywords_number)
                result.append(list(map(lambda x: x[0], keywords)))

        return jsonify({'post_ids' : post_id, 'keywords' : result})
    except Exception as e:
        return str(e)

@app.route('/api/bertopic', methods=['GET'])
def bertopic_extractor():
    try:
        # Get data
        keywords_number = ast.literal_eval(request.args.get('keywords_number'))
        post_id = ast.literal_eval(request.args.get('post_ids'))
        posts_content = ast.literal_eval(request.args.get('posts_content'))

        # Clean post content
        posts_content = map(remove_html, posts_content)
        posts_content = map(remove_between_square_brackets, posts_content)
        posts_content = map(remove_post_id, posts_content)
        posts_content = map(remove_backslash_symbols, posts_content)
        posts_content = list(posts_content)

        # extract keywords
        topics = topic_model.transform(posts_content)
        keywords = [topic_model.get_topic(topic_number) for topic_number in topics[0]]
        result = [list(map(lambda x: x[0], post_keyword))[:keywords_number] for post_keyword in keywords]

        return jsonify({'post_ids' : post_id, 'keywords' : result})
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)