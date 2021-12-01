from pydantic import BaseModel, validator
from typing import List, Union
import ast

# Class which describes Topic measurements
class TopicData(BaseModel):
    """generic class for topic data types

    Attributes:
        keywords_number: number of keywords will be extracted
        post_ids: list of  posts id
        posts_content: list of posts content
    """
    keywords_number: str
    post_ids: List[Union[str, int]]
    posts_content: List[str]

    @validator('keywords_number')
    def keywords_number_must_be_grater_than_zero(cls, v):
        """check for keywords_number grater than zero"""
        if ast.literal_eval(v) <= 0:
            raise ValueError('must be grater than zero')
        return v

    @validator('keywords_number')
    def keywords_number_must_be_int_if_grater_than_one(cls, v):
        """check for keywords_number to be int if grater than one"""
        if ast.literal_eval(v) >= 1 and isinstance(ast.literal_eval(v), float):
            raise ValueError('must be int if grater than one')
        return v

# Class which describes KeyWord measurements
class KeyWordData(BaseModel):
    """generic class for topic data types

    Attributes:
        keywords_number: number of keywords will be extracted
        post_ids: list of  posts id
        posts_content: list of posts content
    """
    keywords_number: str
    post_ids: List[Union[str, int]]
    posts_content: List[str]

    @validator('keywords_number')
    def keywords_number_must_be_grater_than_zero(cls, v):
        """check for keywords_number grater than zero"""
        if ast.literal_eval(v) <= 0:
            raise ValueError('must be grater than zero')
        return v

    @validator('keywords_number')
    def keywords_number_must_be_int_if_grater_than_one(cls, v):
        """check for keywords_number to be int if grater than one"""
        if ast.literal_eval(v) >= 1 and isinstance(ast.literal_eval(v), float):
            raise ValueError('must be int if grater than one')
        return v
