import warnings
import snowflake.connector as sf
from snowflake.connector import DictCursor
from configs.credentials import snowflake_login

from fastapi.testclient import TestClient
from app import app
client = TestClient(app)

def test_snowflake_connection():
    try:
        snowflake_connector = sf.connect(
            user=snowflake_login['username'],
            password=snowflake_login['password'],
            account=snowflake_login['account']
        )
        snowflake_connector.close()
        assert True
    except:
        assert False


def test_ping():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == 'pong'


def test_bertopic_keywords_number_less_than_zero():
    response = client.post("/api/bertopic", json={"keywords_number": -1, "post_ids": ["99918_WP", "99917_WP"], "posts_content": ["As a big sister to four very sweet, hilarious, and very active younger brothers", "If there was one thing you learned by a young age"]})
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'keywords_number'], 'msg': 'must be grater than zero', 'type': 'value_error'}]}

def test_bertopic_keywords_number_must_be_int_if_grater_than_one():
    response = client.post("/api/bertopic", json={"keywords_number": 1.3, "post_ids": ["99918_WP", "99917_WP"], "posts_content": ["As a big sister to four very sweet, hilarious, and very active younger brothers", "If there was one thing you learned by a young age"]})
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'keywords_number'], 'msg': 'must be int if grater than one', 'type': 'value_error'}]}

def test_bertopic_keywords_sample_request():
    warnings.filterwarnings("ignore")
    response = client.post("/api/bertopic", json={"keywords_number": 2, "post_ids": ["99918_WP", "99917_WP"], "posts_content": ["As a big sister to four very sweet, hilarious, and very active younger brothers", "If there was one thing you learned by a young age"]})
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"post_ids":["99918_WP","99917_WP"],"keywords":[["pain","day"],["pain","day"]]}


def test_keybert_keywords_number_less_than_zero():
    response = client.post("/api/autokeyword", json={"keywords_number": -1, "post_ids": ["99918_WP", "99917_WP"], "posts_content": ["As a big sister to four very sweet, hilarious, and very active younger brothers", "If there was one thing you learned by a young age"]})
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'keywords_number'], 'msg': 'must be grater than zero', 'type': 'value_error'}]}

def test_keybert_keywords_number_must_be_int_if_grater_than_one():
    response = client.post("/api/autokeyword", json={"keywords_number": 1.3, "post_ids": ["99918_WP", "99917_WP"], "posts_content": ["As a big sister to four very sweet, hilarious, and very active younger brothers", "If there was one thing you learned by a young age"]})
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['body', 'keywords_number'], 'msg': 'must be int if grater than one', 'type': 'value_error'}]}

def test_keybert_keywords_sample_request():
    warnings.filterwarnings("ignore")
    response = client.post("/api/autokeyword", json={"keywords_number": 2, "post_ids": ["99918_WP", "99917_WP"], "posts_content": ["As a big sister to four very sweet, hilarious, and very active younger brothers", "If there was one thing you learned by a young age"]})
    assert response.status_code == 200
    assert response.json() == {"post_ids":["99918_WP","99917_WP"],"keywords":[["sister sweet hilarious","active younger brothers"],["learned young age","thing"]]}