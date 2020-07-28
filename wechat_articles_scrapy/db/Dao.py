from wechat_articles_scrapy.db.MysqlUtil import MysqlUtil
from elasticsearch_dsl import Text, Date, Keyword, Integer, Document, Completion
from elasticsearch_dsl import analyzer
from elasticsearch_dsl.connections import connections
from elasticsearch import Elasticsearch, ConflictError
import logging
from scrapy.utils.project import get_project_settings


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
    def insert_img_video(connector, fakeid, article_id, path, info, typee):
        insert_sql = """
                        insert into wx_img_video(fakeid, article_id, path, result, type) VALUES (%s,%s,%s,%s,%s)
                     """
        connector.insert_one(insert_sql, (fakeid, article_id, path, info, typee))

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

    client = Elasticsearch(hosts=[settings.get('ES_HOST')])

    def __init__(self):
        pass

    @property
    def logger(self):
        logger = logging.getLogger(self.name)
        return logging.LoggerAdapter(logger, {'ESDao': self})

    def add_doc(self, doc_id, index, body):
        try:
            result = self.client.create(index=index, id=doc_id, body=body)
            self.logger.info(result)
        except ConflictError:
            self.logger.error(f"文档已存在---------------index[{index}]----doc_id[{doc_id}]")


if __name__ == '__main__':
    result = MysqlDao.get_count_by_articleid('2650378464_1')
    print(result)







