import json
import os
import re
import time

from bs4 import BeautifulSoup, Tag
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
    #         img_cover_url = 'http://hahaha/abc.jpg'
    #         video_url = 'http://hahaha/abc.mp4'
    #         new_video_tag = art_html.new_tag("video",
    #                                          attrs={'width': '323px', 'height': '194px', 'poster': img_cover_url,
    #                                                 'class': 'video_iframe rich_pages', 'controls': 'controls',
    #                                                 'autoplay': 'autoplay'})
    #         new_source_tag = art_html.new_tag("source", attrs={'src': video_url, 'type': 'video/mp4'})
    #         new_video_tag.append(new_source_tag)
    #         ifr.insert_after(new_video_tag)
    #         ifr.extract()
    # print(art_html.prettify())
    # print(uuid.uuid1())

    # test()

    html_str = "<html><iframe calss = '' vid = '1' src = 'a'><video class='abc' /></iframe><iframe vid = '2'>" \
               "<video class='def' /></iframe><video class = 'hh'/><div class = 'js_poster_cover' " \
               "style='background-image:url(http://mmbiz.qpic.cn/mmbiz_jpg/Jm72lU1B4dOrCDNALgrEyCNJHpxjRT7zwWicfNf0EwTJ9C9jJxiaGNN93RZuBibwuWAYG4j9jIQWKVGRZw0XZa9UA/0?wx_fmt=jpeg);-webkit-background-size:cover;background-size:cover;'/></html>"
    art_html = BeautifulSoup(html_str, 'lxml')
    ifr_arr = art_html.find_all('iframe')
    # for ifr in ifr_arr:
        # video_arr = ifr.find_all('video')
        # video_arr[0].attrs['flag'] = '1'
        # print(str(ifr))
    # div_ = art_html.find('div')
    # back_ground_url = re.findall('ural\((.*?)\)', str(div_))
    # print(back_ground_url)
    #
    # a = {'a1': 'b'}
    # print(a['a1'] is not 'b')
    #
    # lst = ['a', 'a', 'b', 'c']
    # print(set(lst))
    # h = 'http://www.baidu.com/abc/efe/kjk/lll.jpg'
    # dct = {h: lst, 'a': 'g'}
    # d = dct[h]
    # d.append('g')
    # print(len(dct))
    #
    # div_.attrs['style'] = 'joke'
    # print(div_)
    s = 'background-image: url("//vpic.video.qq.com/-96655397/v3128pedn9w.png"); background-size: cover;url()'
    backkgd_url = re.findall('url\("(.+?)"\)', s)
    print(backkgd_url[0])
    # print(art_html.prettify())
    # video_arr = art_html.find_all('video')
    # a : Tag
    #
    # for video_temp in video_arr:
    #     if video_temp.parent.previous_sibling is not None:
    #         style = video_temp.parent.parent.find('div', {'class': 'js_poster_cover'})['style']
    #         back_ground_url = re.findall('url\((.*?)\)', style)
    #         print(back_ground_url)

    # from selenium import webdriver
    # from pyquery import PyQuery as pq
    #
    # base_dir = os.path.dirname(__file__)
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--disable-gpu')
    # browser = webdriver.Chrome(options=chrome_options)
    # # browser.implicitly_wait(10)
    # browser.get('https://mp.weixin.qq.com/s?__biz=MzUzNTAxODAzMA==&mid=2247495653&idx=2&sn=9b9ee2f2ab71f6f908b3af582d81b4c2&chksm=fa8940a4cdfec9b2851ff19ca5deb7c0cda34b9850ce41df10478f22656f21243d8b9a77e4c4#rd')
    # # 可以看到获取的源码都是些js与css语句，dom并未生成，需要模拟浏览器滚动来生成dom：？？？
    # for i in range(1, 11):
    #     browser.execute_script(
    #         "window.scrollTo(0, document.body.scrollHeight/10*%s);" % i
    #     )
    #     time.sleep(0.1)
    # data = browser.page_source.encode('utf-8')
    # # 现在获取的源码基本是完整的，还存在一些小问题，比如网页为了让img延迟加载，img的地址是放在data-img属性上的，等到浏览器滑动至图片时才修改src属性，可以使用pyquery修改
    # doc = pq(data)
    # for img in doc('img'):
    #     img = pq(img)
    #     if img.attr['data-img']:
    #         img.attr.src = img.attr['data-img']
    # data = doc.html(method='html').replace('src="//', 'src="http://')
    # f = open('D:/detail.html', 'w', encoding='utf-8')
    # f.write(bytes(data, encoding='utf-8').decode())
    # f.close()
