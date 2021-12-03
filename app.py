import warnings
warnings.filterwarnings("ignore")

import ast
import logging
from datetime import datetime
from utils.get_data import get_posts
from data_queries.snowflake_query import get_snowflake_query

import tqdm
tqdm.tqdm.pandas()

from utils.clean_text import preprocess_keywords, preprocess_topic
from configs.api import api_config

# keyword extraction
from keybert import KeyBERT
kw_extraction_model = KeyBERT()

# topic extraction
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer

vectorizer_model= CountVectorizer(ngram_range=(1, 3), stop_words="english")
topic_model = BERTopic(vectorizer_model=vectorizer_model)
topic_model = topic_model.load('models_artifact/BERTopic_WP_2021_12_03_15_16_29.bin')

# API configuration
PORT = api_config['port']
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_formats.AutoTagging import KeyWordData, TopicData, TopicRetrainSite

logging.basicConfig(level=logging.DEBUG)

# App description
description = """
AutoTagging API helps you do awesome stuff. 🚀
## bertopic_extractor
You can **assign topic to posts**.
## keyword_extractor
You will be able to:
You can **extract kaywords from posts**.
"""

# Create the app object
app = FastAPI(
    title="AutoTaggingAPI",
    description=description,
    version="0.0.1",
    contact={
        "name": "Andrii Bratun",
        "email": "andrii.bratun@.health-union.com",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/', tags=["ping_pong"], summary="Check if API response to query", include_in_schema=False)
def ping():
    return 'pong'

@app.post('/api/bertopic', tags=["topic"], summary="Extract topic keywords from posts")
def bertopic_extractor(data: TopicData):
    """
    Extract topic keywords from posts using BERTopic model:

    - **keywords_number**: amount of returned keywords, if int - number of top keywords, if float and less than 1 - return all keywords above threshold
    - **post_ids**: list of string post ids
    - **posts_content**: list of string post content

    Sample input:
     - {"keywords_number": 2, "post_ids": ["99918_WP", "99917_WP"], "posts_content": ["As a big sister to four very sweet, hilarious, and very active younger brothers", "If there was one thing you learned by a young age"]}

    Sample output:
     - {"post_ids":["99918_WP","99917_WP"],"keywords":[["pain","day"],["pain","day"]]}

    """
    try:
        # Get data
        data = data.dict()
        keywords_number = ast.literal_eval(data['keywords_number'])
        post_ids = data['post_ids']
        posts_content = data['posts_content']

        # Clean post content
        posts_content = preprocess_topic(posts_content)

        # extract keywords
        topics = topic_model.transform(posts_content)
        keywords = [topic_model.get_topic(topic_number) for topic_number in topics[0]]

        # scale keywords (divide each score on max score)
        keywords = [[(k, w / k_score[0][1]) for k, w in k_score] for k_score in keywords]

        if keywords_number < 1:
            # filter all keywords with score grater than threshold
            result = [tuple(filter(lambda x: x[1] > keywords_number, post_keyword)) for post_keyword in keywords]
            result = [list(map(lambda x: x[0], post_keyword)) for post_keyword in result]
        else:
            # filter top keywords
            result = [list(map(lambda x: x[0], post_keyword))[:keywords_number] for post_keyword in keywords]

        return {'post_ids': post_ids, 'keywords': result}

    except Exception as e:
        return str(e)

@app.post('/api/bertopic_train', tags=["topic"], summary="train new model for specified disease")
def bertopic_train(data: TopicRetrainSite):
    """
    Train new model for specified disease on a new data

    - **site**: name of the site

    Sample input:
     - {"site": "RA"}

    Sample output:
     - 'Training was succes'
    """
    try:
        # Get data
        site = data.dict()['site']
        query = get_snowflake_query(site)
        posts_df = get_posts(query)

        if posts_df.empty:
            return 'site does not have any posts!'

        # Clean post content
        preprocessed_posts = preprocess_topic(posts_df.POST_CONTENT.tolist())

        # Define model
        vectorizer_model = CountVectorizer(ngram_range=(1, 3), stop_words="english")
        topic_model = BERTopic(vectorizer_model=vectorizer_model)

        # Train model
        topic_model.fit(preprocessed_posts)

        # Save model
        topic_model.save(f'models_artifact/BERTopic_{site}_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.bin')

        return 'Training was succes'

    except Exception as e:
        return str(e)

@app.post('/api/autokeyword', tags=["keywords"], summary="Extract keywords from posts")
def keyword_extractor(data: KeyWordData):
    """
    Extract keywords from posts using KeyBERT model:

    - **keywords_number**: amount of returned keywords, if int - number of top keywords, if float and less than 1 - return all keywords above threshold
    - **post_ids**: list of string post ids
    - **posts_content**: list of string post content

    Sample input:
     - {"keywords_number": 2, "post_ids": ["99918_WP", "99917_WP"], "posts_content": ["As a big sister to four very sweet, hilarious, and very active younger brothers", "If there was one thing you learned by a young age"]}

    Sample output:
     - {"post_ids":["99918_WP","99917_WP"],"keywords":[["sister sweet hilarious","active younger brothers"],["learned young age","thing"]]}
  """

    try:
        # Get data
        data = data.dict()
        keywords_number = ast.literal_eval(data['keywords_number'])
        post_ids = data['post_ids']
        posts_content = data['posts_content']

        # Clean post content
        posts_content = preprocess_keywords(posts_content)

        # extract keywords
        result = []

        if keywords_number < 1:
            for post_content in posts_content:
                keywords = kw_extraction_model.extract_keywords(post_content, keyphrase_ngram_range=(1, 3),
                                                                stop_words='english', use_mmr=True, diversity=0.5,
                                                                top_n=20)
                keywords.sort(key=lambda x: x[1], reverse=True)
                # filter all keywords with score grater than threshold
                filtered_keywords = list(filter(lambda x: x[1] > keywords_number, keywords))
                if len(filtered_keywords) == 0:
                    result.append(['No keywords above specified threshold'])
                else:
                    result.append(list(map(lambda x: x[0], filtered_keywords)))

        else:
            for post_content in posts_content:
                keywords = kw_extraction_model.extract_keywords(post_content, keyphrase_ngram_range=(1, 3),
                                                                stop_words='english', use_mmr=True, diversity=0.5,
                                                                top_n=keywords_number)
                keywords.sort(key=lambda x: x[1], reverse=True)
                # Get top keywords
                result.append(list(map(lambda x: x[0], keywords)))

        return {'post_ids': post_ids, 'keywords': result}

    except Exception as e:
        return str(e)


# # Run the API with uvicorn
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=PORT)

# uvicorn app:app --reload