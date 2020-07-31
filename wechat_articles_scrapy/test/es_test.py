import re
import time

import requests
from bs4 import BeautifulSoup
from elasticsearch_dsl import Text, Date, Keyword, Integer, Document, Completion
from elasticsearch_dsl import analyzer
from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch, ConflictError
import uuid

connections.create_connection(hosts=["localhost"])

my_analyzer = analyzer('ik_smart')

client = Elasticsearch(hosts=["localhost"])


class PeopleIndex(Document):
    name = Text(analyzer="ik_max_word")
    age = Integer()
    sex = Keyword()

    class Index:
        name = 'people'


if __name__ == '__main__':
    # response = []
    # response = client.search(
    #     index="people",
    #     request_timeout=60,
    #     body={
    #         "query": {
    #             "multi_match": {
    #                 "query": '小明',
    #                 "fields": ["name", "sex"]
    #             }
    #         }
    #     }
    # )
    # print("--查询结束--")
    # for hit in response["hits"]["hits"]:
    #     print("score:", hit['_score'], "source:", hit['_source'])
    # try:
    #     c_re = client.create(index="people", id='2', body={
    #                       "name": "张磊",
    #                       "age": 22,
    #                       "sex": "男",
    #                       "dess": "这是一个测试"
    #                     })
    #     print(c_re)
    # except ConflictError:
    #     print("文档已存在")
    print(type(None))











