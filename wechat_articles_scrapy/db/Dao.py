import json
import logging

from elasticsearch import Elasticsearch, ConflictError
from redis import StrictRedis
from scrapy.utils.project import get_project_settings

from wechat_articles_scrapy.db.MysqlUtil import MysqlUtil


class MysqlDao:

    @staticmethod
    def get_count_by_articleid(article_id):
        connector = MysqlUtil()
        get_count_sql = """
                          select count(*) from wx_article_info where article_id = %s 
                        """
        result = connector.get_all(get_count_sql, [article_id])
        return result[0][0]

    @staticmethod
    def get_wxconfig():
        connector = MysqlUtil()
        sele_one_sql = 'select * from wx_config'
        return connector.get_one(sele_one_sql)

    @staticmethod
    def insert_article(connector, item):
        insert_sql = """
                        insert into wx_article_info(fakeid, article_id, title, digest, link, cover_url, create_time_wx) 
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                     """
        connector.insert_one(insert_sql,
                             (item['fakeid'],
                              item['article_id'],
                              item['title'],
                              item['digest'],
                              item['link'],
                              item['cover_url'],
                              item['create_time_wx']))

    @staticmethod
    def insert_img_video(connector, params):
        insert_sql = """
                        insert into wx_img_video(fakeid, article_id, path, result, type, video_type, video_vid) VALUES (%s,%s,%s,%s,%s,%s,%s)
                     """
        connector.insert_one(insert_sql, (params["fakeid"], params["article_id"], params["path"], params["info"],
                                          params["type"], params["video_type"], params["video_vid"]))

    @staticmethod
    def update_article_content(connector, article_id, content):
        update_sql = """
                        update wx_article_info set content = %s where article_id = %s
                     """
        connector.update(update_sql, (content, article_id))


class ESDao:
    name = "ESDao"

    # 获取setting文件中的配置
    settings = get_project_settings()

    _client = Elasticsearch(hosts=[settings.get('ES_HOST')])

    def __init__(self):
        pass

    @property
    def logger(self):
        logger = logging.getLogger(self.name)
        return logging.LoggerAdapter(logger, {'ESDao': self})

    def add_doc(self, doc_id, index, body):
        try:
            result = self._client.create(index=index, id=doc_id, body=body)
            self.logger.info(result)
        except ConflictError:
            self.logger.error(f"文档已存在---------------index[{index}]----doc_id[{doc_id}]")


class RedisDao:
    name = "RedisDao"
    # 获取setting文件中的配置
    settings = get_project_settings()
    _redis = StrictRedis(host=settings.get('REDIS_HOST'), port=settings.get('REDIS_PORT'), db=0, password=None)

    @classmethod
    def exists(cls, name: str):
        return cls._redis.exists(name)

    @classmethod
    def hset_one(cls, name: str, key: str, value):
        cls._redis.hset(name, key, value)

    @classmethod
    def hset_batch(cls, name: str, dic: dict):
        for k, v in dic.items():
            cls._redis.hset(name, k, v)

    @classmethod
    def hget_one(cls, name: str, key: str):
        return cls._redis.hget(name, key)

    @classmethod
    def hget_all(cls, name: str):
        return cls._redis.hgetall(name)

    @classmethod
    def hexists(cls, name: str, key: str):
        return cls._redis.hexists(name, key)

    @classmethod
    def exists_name(cls, name: str):
        return cls._redis.exists(name)

    @classmethod
    def expire(cls, name: str, secds):
        cls._redis.expire(name, secds)

    def __init__(self):
        pass


if __name__ == '__main__':
    # result = MysqlDao.get_count_by_articleid('2650378464_1')
    test = {'test': 'test'}
    old = RedisDao.hget_one('MzUzNTAxODAzMA==2247495057_1', 'img_video_cover')
    print(old)
