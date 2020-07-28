# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
import hashlib
import json
import os

import emoji
import pymongo
from scrapy import Request
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.misc import md5sum
from scrapy.utils.python import to_bytes

from wechat_articles_scrapy.db.Dao import MysqlDao, ESDao
from wechat_articles_scrapy.db.MysqlUtil import MysqlUtil
from wechat_articles_scrapy.items import ArticleInfoItem, ImgDownloadItem, videoDownloadItem
from wechat_articles_scrapy.util.DateUtil import DateUtil

# settings = get_project_settings()

check_file = "isRunning.txt"


class ArticleInfoPipeline:

    def open_spider(self, spider):
        spider.logger.debug('--------spider_article_info------------start')
        # with open(check_file, "w") as cfile:  # 创建一个文件，代表爬虫在运行中
        #     cfile.close()

    def process_item(self, item, spider):
        if isinstance(item, ArticleInfoItem):
            connector = MysqlUtil()
            MysqlDao.insert_article(connector, item)
            connector.end()
        return item

    def close_spider(self, spider):
        spider.logger.debug('--------spider_article_info------------end')
        # file_exist = os.path.isfile(check_file)
        # if file_exist:
        #     os.remove(check_file)


class ImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        return '%s/%s.%s' % (DateUtil.curDate1(), image_guid, 'gif' if 'gif' in request.url else 'jpg')

    def get_media_requests(self, item, info):
        if isinstance(item, ImgDownloadItem):
            for index, img_url in enumerate(item['image_urls']):
                yield Request(img_url, meta={'item': item, 'index': index})

    def check_gif(self, image):
        if image.format is None:
            return True

    def persist_gif(self, key, data, info):
        root, ext = os.path.splitext(key)
        absolute_path = self.store._get_filesystem_path(key)
        self.store._mkdir(os.path.dirname(absolute_path), info)
        f = open(absolute_path, 'wb')  # use 'b' to write binary data.
        f.write(data)

    def image_downloaded(self, response, request, info):
        checksum = None
        for path, image, buf in self.get_images(response, request, info):
            if checksum is None:
                buf.seek(0)
                checksum = md5sum(buf)
            width, height = image.size
            # self.logger.debug(f'-----------是否gif-------------{self.check_gif(image)}')
            if self.check_gif(image):
                self.persist_gif(path, response.body, info)
            else:
                self.store.persist_file(
                    path, buf, info,
                    meta={'width': width, 'height': height},
                    headers={'Content-Type': 'image/jpeg'})
        return checksum


class ImageSavePipeline(object):

    def __init__(self, mongo_uri, mongo_db, mongo_port, server_url):
        # 初始化方法__new__:构造方法，在内存中开辟一块空间
        self.client = pymongo.MongoClient(mongo_uri, mongo_port)
        self.db = self.client[mongo_db]
        self.server_url = server_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB'),
            mongo_port=crawler.settings.get('MONGO_PORT'),
            server_url=crawler.settings.get('SELF_BASE_SERVER_URL')
        )

    def process_item(self, item, spider):
        if isinstance(item, ImgDownloadItem):
            img_tag_list = item['img_tag_list']
            images = item['images']
            # spider.logger.debug(f'数量是否相同：--------------------{len(img_tag_list) == len(images)}')
            if item["img_poz"] is not "1" and len(img_tag_list) == len(images) and len(img_tag_list) != 0:
                for re_tmp in images:
                    if 'checksum' in re_tmp:
                        del re_tmp['checksum']
                    if 'status' in re_tmp:
                        del re_tmp['status']
                    re_tmp['path'] = self.server_url + '/images/' + re_tmp['path']

                for ind in range(len(img_tag_list)):
                    if 'data-src' in img_tag_list[ind].attrs:
                        img_tag_list[ind].attrs['data-src'] = images[ind]['path']
                    elif 'src' in img_tag_list[ind].attrs:
                        img_tag_list[ind].attrs['src'] = images[ind]['path']
                connector = MysqlUtil()
                MysqlDao.insert_img_video(connector, item['fakeid'], item['article_id'], '', json.dumps(images), '1')
                # MysqlDao.update_article_content(connector, item['article_id'],
                #                                 emoji.demojize(str(item['soup_html'])))
                connector.end()
                es_dao = ESDao()
                es_dao.add_doc(item['article_id'], "wxat",
                               {"article_id": item['article_id'], "title": item['title'],
                                "digest": item['digest'], "content": emoji.demojize(str(item['soup_html'])),
                                "@timestamp": datetime.datetime.now(), "@version": "1.0"})
                # MONGO表名为wx_img_video，插入数据
                # self.db['wx_img_video'].insert_one({'fakeid': item['fakeid'], 'article_id': item['article_id'],
                #                                     'path': '', 'result': json.dumps(images), 'type': '1'})
            elif item["img_poz"] is "1":
                connector = MysqlUtil()
                MysqlDao.insert_img_video(connector, item['fakeid'], item['article_id'], '', json.dumps(images), '3')
                connector.end()
        return item

    def close_spider(self, spider):
        # self.client.close()
        pass


class VideoDownloadPipeline(FilesPipeline):
    # 修改file_path方法，使用提取的文件名保存文件
    def file_path(self, request, response=None, info=None):
        # 获取到Request中的item
        item = request.meta['item']
        # 文件URL路径的最后部分是文件格式
        file_type = 'mp4'
        file_name = hashlib.sha1(to_bytes(request.url)).hexdigest()
        # 修改使用item中保存的文件名作为下载文件的文件名，文件格式使用提取到的格式
        file_name = u'{0}/{1}.{2}'.format(DateUtil.curDate1(), file_name, file_type)
        return file_name

    def get_media_requests(self, item, info):
        if isinstance(item, videoDownloadItem):
            for file_url in item['file_urls']:
                # 为request带上meta参数，把item传递过去
                yield Request(file_url, meta={'item': item})


class VideoSavePipeline(object):

    def __init__(self, mongo_uri, mongo_db, mongo_port, server_url):
        # 初始化方法__new__:构造方法，在内存中开辟一块空间
        self.client = pymongo.MongoClient(mongo_uri, mongo_port)
        self.db = self.client[mongo_db]
        self.server_url = server_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB'),
            mongo_port=crawler.settings.get('MONGO_PORT'),
            server_url=crawler.settings.get('SELF_BASE_SERVER_URL')
        )

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        if isinstance(item, videoDownloadItem) and item['files']:
            video_url = self.server_url + '/video/' + item['files'][0]['path']
            connector = MysqlUtil()
            MysqlDao.insert_img_video(connector, item['fakeid'], item['article_id'], video_url
                                      , json.dumps(item['files']), '2')
            connector.end()
            # MONGO表名为wx_img_video，插入数据
            # self.db['wx_img_video'].insert_one({'fakeid': item['fakeid'], 'article_id': item['article_id'],
            #                                     'path': video_url, 'result': json.dumps(item['files']),
            #                                     'type': '2'})

    def close_spider(self, spider):
        # self.client.close()
        pass

# class LvyouPipeline(object):
#     """
#     异步更新操作
#     """
#
#     def __init__(self, dbpool):
#         self.dbpool = dbpool
#
#     @classmethod
#     def from_settings(cls, settings):  # 函数名固定，会被scrapy调用，直接可用settings的值
#         """
#         数据库建立连接
#         :param settings: 配置参数
#         :return: 实例化参数
#         """
#         adbparams = dict(
#             host=settings['MYSQL_HOST'],
#             db=settings['MYSQL_DATABASE'],
#             user=settings['MYSQL_USER'],
#             password=settings['MYSQL_PASSWORD'],
#             cursorclass=pymysql.cursors.DictCursor  # 指定cursor类型
#         )
#
#         # 连接数据池ConnectionPool，使用pymysql或者Mysqldb连接
#         dbpool = adbapi.ConnectionPool('pymysql', **adbparams)
#         # 返回实例化参数
#         return cls(dbpool)
#
#     def process_item(self, item, spider):
#         """
#         使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
#         """
#         query = self.dbpool.runInteraction(self.do_insert, item)  # 指定操作方法和操作数据
#         # 添加异常处理
#         query.addCallback(self.handle_error)  # 处理异常
#
#     def do_insert(self, cursor, item):
#         # 对数据库进行插入操作，并不需要commit，twisted会自动commit
#         insert_sql = "insert into test(name, age, url, info, img_path) VALUES (%s,%s,%s,%s,%s)"
#         cursor.execute(insert_sql,
#                        (item['image_name'],
#                         '10',
#                         item['image_urls'],
#                         str(item['images'][0]),
#                         item['images'][0]['path']))
#
#     def handle_error(self, failure):
#         if failure:
#             # 打印错误信息
#             print(failure)
#
#
# class LvyouPipeline(object):
#     """
#     同步更新操作
#     """
#
#     def __init__(self):
#         # connection database
#         self.connect = pymysql.connect(host='XXX', user='root', passwd='XXX',
#                                        db='scrapy_test')  # 后面三个依次是数据库连接名、数据库密码、数据库名称
#         # get cursor
#         self.cursor = self.connect.cursor()
#         print("连接数据库成功")
#
#     def process_item(self, item, spider):
#         # sql语句
#         insert_sql = "insert into test(name, age, url, info, img_path) VALUES (%s,%s,%s,%s,%s)"
#         self.cursor.execute(insert_sql,
#                             (item['image_name'],
#                              '10',
#                              item['image_urls'],
#                              str(item['images'][0]),
#                              item['images'][0]['path']))
#         # 提交，不进行提交无法保存到数据库
#         self.connect.commit()
#
#     def close_spider(self, spider):
#         # 关闭游标和连接
#         self.cursor.close()
#         self.connect.close()
#
#
# class MysqlUtilPipeline(object):
#     """
#     使用工具类操作数据
#     """
#
#     def __init__(self):
#         # connection database
#         self.connector = MysqlUtil()
#         print("连接数据库成功")
#
#     def process_item(self, item, spider):
#         # 开始事务
#         # self.connector.begin()
#         # sql语句
#         insert_sql = "insert into test(name, age, url, info, img_path) VALUES (%s,%s,%s,%s,%s)"
#         self.connector.insert_one(insert_sql,
#                                   (item['image_name'],
#                                    '10',
#                                    item['image_urls'],
#                                    str(item['images'][0]),
#                                    item['images'][0]['path']))
#         # 提交事务
#         self.connector.end()
#
#     def close_spider(self, spider):
#         # 回收资源
#         # print('回收资源')
#         # self.connector.dispose()
#         pass
