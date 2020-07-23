import requests
from bs4 import BeautifulSoup
from elasticsearch_dsl import Text, Date, Keyword, Integer, Document, Completion
from elasticsearch_dsl import analyzer
from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch
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

    # c_re = client.create(index="people", id=uuid.uuid1(), body={
    #                   "name": "张磊",
    #                   "age": 22,
    #                   "sex": "男",
    #                   "dess": "这是一个测试"
    #                 })
    # print(c_re)
    # pass
    arturl = "https://mp.weixin.qq.com/s?__biz=MzA4MTM1NDcxMA==&mid=2650376956&idx=1&sn=64749e57c1b684e70b1f26fbd6f98e29&chksm=879b6045b0ece953ad3dd7316edbb0cd6f263fd2286c770b0a216ac69771e21b0553f2b4cb48&mpshare=1&srcid=07222eBRlFfXoIfgzT46fVTt&sharer_sharetime=1595407653440&sharer_shareid=40bf552b62a64ccd008e389d94cc5e23&from=singlemessage&scene=1&subscene=10000&clicktime=1595415668&enterid=1595415668&ascene=1&devicetype=android-29&version=2700103f&nettype=3gnet&abtest_cookie=AAACAA%3D%3D&lang=zh_CN&exportkey=AYDHuJe1szBZMU3Am%2Boh4co%3D&pass_ticket=qM9j5N%2FkGqF8ijxXHxYb8rdp6%2B%2Bavh7hOwu1KabhxBmhCghgHL7H3S4cwJYM%2BL8b&wx_header=1"
    artresp = requests.get(url=arturl)
    print(type(artresp))
    art_html = BeautifulSoup(artresp.content, 'lxml')
    ifr_arr = None
    if ifr_arr:
        print("some")
    else:
        print("kong")











