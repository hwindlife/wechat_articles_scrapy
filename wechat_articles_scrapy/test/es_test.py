import json
import time

from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Text, Keyword, Integer, Document
from elasticsearch_dsl import analyzer
from elasticsearch_dsl.connections import connections

from wechat_articles_scrapy.db.Dao import RedisDao

connections.create_connection(hosts=["localhost"])

my_analyzer = analyzer('ik_smart')

client = Elasticsearch(hosts=["localhost"])


class PeopleIndex(Document):
    name = Text(analyzer="ik_max_word")
    age = Integer()
    sex = Keyword()

    class Index:
        name = 'people'


def test():
    from redis import StrictRedis
    # art_dict = {'name': '哈哈哈', 'age': '18', 'hobby': 'movie'}
    # RedisDao.hset_one('wxart_20200811', '123_456', json.dumps(art_dict))
    # RedisDao.expire('wxart_20200811', 36000)
    # print(RedisDao.hget_one('wxart_20200811', '123_456'))
    # a = RedisDao.hget_one('wxart_20200811', '123_456')
    # img = [{'url': 'a.jpg', 'vid': '123'}, {'url': 'a.jpg', 'vid': '123'}]
    # a_json = json.loads(a)
    # a_json['imgInfo'] = img
    # RedisDao.hset_one('wxart_20200811', '123_456', json.dumps(a_json))
    # time.sleep(1)
    # print(RedisDao.hget_one('wxart_20200811', '123_456'))
    redis = StrictRedis(host='localhost', port=6379, db=0, password=None)
    # redis.lpush('dl', 'a')
    # redis.lpush('dl', 'b')
    # redis.lpush('dl', 'c')
    # print(redis.rpop('dl'))
    # print(redis.llen('dl'))
    for i in range(10):
        redis.lpush('dl', i)
    redis.ltrim('dl', 0, 5)
    print(redis.llen('dl'))
    rd = RedisDao()




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
    # print(type(None))

    # # 获取签名
    # type = "0"  # 0：共有，1：私有
    # days = "0"  # 保存天数 0：永久
    # file_info = {'signNum': '1', 'cosStr': 'scrapy_wxfile', 'type': 'jpg'}
    # url = 'https://ssp.taikang.com/cos/getSignV5'
    # resp = HttpUtils.post_json(url, {'type': type, 'days': days, 'list': [file_info]})
    # resp_json = resp.json()
    # if resp_json['rspCode'] == "0":
    #     file_auth = resp_json['info']['list'][0]['authList'][0]
    #     print(file_auth['cosPath'])
    #     print(file_auth['reqUrl'])
    #     print(file_auth['authStr'])
    #     # 推送文件到腾讯云
    #     HttpUtils.put_binary(file_auth['reqUrl'],
    #                          {'Authorization': file_auth['authStr'], 'Content-Type': 'binary'},
    #                          'D:/construct.jpg')

    # html_str = "<html><iframe calss = '' vid = '1' src = ''></iframe><iframe vid = '2'></iframe></html>"
    # art_html = BeautifulSoup(html_str, 'lxml')
    # ifr_arr = art_html.find_all('iframe')
    # if ifr_arr:
    #     for ifr in ifr_arr:
    #         new_video_tag = art_html.new_tag("video", attrs={'width': '323px', 'height': '194px', 'poster': '',
    #                                                          'class': 'video_iframe rich_pages', 'controls': 'controls',
    #                                                          'autoplay': 'autoplay'})
    #         new_source_tag = art_html.new_tag("source", attrs={'src': '', 'type': 'video/mp4'})
    #         new_video_tag.append(new_source_tag)
    #         ifr.insert_after(new_video_tag)
    #         ifr.extract()
    # print(art_html.prettify())

    test()
