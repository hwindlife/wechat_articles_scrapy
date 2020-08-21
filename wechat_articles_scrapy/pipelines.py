# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

import emoji
from scrapy import Request
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.misc import md5sum
from scrapy.utils.project import get_project_settings
from scrapy.utils.python import to_bytes

from wechat_articles_scrapy.db.Dao import RedisDao
from wechat_articles_scrapy.items import ArticleInfoItem, ImgDownloadItem, VideoDownloadItem
from wechat_articles_scrapy.kafka.WxArticlePrd import WxArticlePrd
from wechat_articles_scrapy.util import HttpUtils, txcosutil
from wechat_articles_scrapy.util.DateUtil import DateUtil

settings = get_project_settings()

check_file = "isRunning.txt"


class ArticleInfoPipeline:

    def open_spider(self, spider):
        spider.logger.debug('--------spider_article_info------------start')
        # with open(check_file, "w") as cfile:  # 创建一个文件，代表爬虫在运行中
        #     cfile.close()

    def process_item(self, item, spider):
        if isinstance(item, ArticleInfoItem):
            # connector = MysqlUtil()
            # MysqlDao.insert_article(connector, item)
            # connector.end()
            fakeid = item['fakeid']
            article_id = item['article_id']
            # 推送到kafka
            kfk_mess = {'fakeid': fakeid, 'article_id': article_id, 'title': item['title'],
                        'digest': item['digest'], 'link': item['link'], 'cover_url': item['cover_url'],
                        'create_time_wx': item['create_time_wx'], 'kafka_msg_type': 'list'}
            # WxArticlePrd.send_msg(kfk_mess)
            # 调用kfkapi
            HttpUtils.post_json(settings['API_BASE_URL'] + 'kfkapi/sendMsg', kfk_mess)

            # 存入redis缓存
            redis_key = fakeid + article_id
            RedisDao.hset_one(redis_key, 'title', item['title'])
            RedisDao.expire('wxart_20200811', 60 * 60 * 24 * 30)
        return item

    def close_spider(self, spider):
        pass
        # spider.logger.debug('--------spider_article_info_1------------end')
        # WxArticlePrd.close()
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

    def close_spider(self, spider):
        # spider.logger.debug('--------spider_article_info_2------------end')
        pass


class ImageSavePipeline(object):

    def __init__(self, mongo_uri, mongo_db, mongo_port, server_url):
        # 初始化方法__new__:构造方法，在内存中开辟一块空间
        # self.client = pymongo.MongoClient(mongo_uri, mongo_port)
        # self.db = self.client[mongo_db]
        # self.server_url = server_url
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            # mongo_uri=crawler.settings.get('MONGO_URI'),
            # mongo_db=crawler.settings.get('MONGO_DB'),
            # mongo_port=crawler.settings.get('MONGO_PORT'),
            # server_url=crawler.settings.get('SELF_BASE_SERVER_URL')
        )

    def process_item(self, item, spider):
        if isinstance(item, ImgDownloadItem):
            img_tag_list = item['img_tag_list']
            images = item['images']
            # spider.logger.debug(f'数量是否相同：--------------------{len(img_tag_list) == len(images)}')
            if item["img_poz"] is not "1" and len(img_tag_list) == len(images) and len(img_tag_list) != 0:
                # 多线程推送图片到腾讯云，且缓存推送结果
                push_cos_result_arr = []
                with ThreadPoolExecutor(max_workers=10) as td_pool:
                    all_task = [td_pool.submit(self.push_to_cos, '/'.join([settings['IMAGES_STORE'], img_info['path']]),
                                               img_info, push_cos_result_arr) for img_info in images]
                    wait(all_task, return_when=ALL_COMPLETED)
                # 腾讯云图片访问链接替换原链接
                for ind in range(len(img_tag_list)):
                    if 'data-src' in img_tag_list[ind].attrs:
                        img_tag_list[ind].attrs['data-src'] = images[ind]['path']
                    elif 'src' in img_tag_list[ind].attrs:
                        img_tag_list[ind].attrs['src'] = images[ind]['path']
                # 调用kfkapi
                params = {"fakeid": item['fakeid'], "article_id": item['article_id'], "path": '',
                          "info": json.dumps(images), "type": '1', "video_type": item['video_type'],
                          "video_vid": item['video_vid'], "kafka_msg_type": "img_content", "title": item['title'],
                          "digest": item['digest'], "content": emoji.demojize(str(item['soup_html']))}
                # connector = MysqlUtil()
                # MysqlDao.insert_img_video(connector, params)
                # connector.end()
                # 推送kafka
                WxArticlePrd.send_msg(params)
                # 插入es
                # es_dao = ESDao()
                # es_dao.add_doc(item['article_id'], "wxat",
                #                {"article_id": item['article_id'], "title": item['title'],
                #                 "digest": item['digest'], "content": emoji.demojize(str(item['soup_html'])),
                #                 "@timestamp": int(time.time()), "@version": "1.0"})
                # MONGO表名为wx_img_video，插入数据
                # self.db['wx_img_video'].insert_one({'fakeid': item['fakeid'], 'article_id': item['article_id'],
                #                                     'path': '', 'result': json.dumps(images), 'type': '1'})
            elif item["img_poz"] is "1":
                params = {"fakeid": item['fakeid'], "article_id": item['article_id'],
                          "path": '/images/' + images[0]['path'], "info": json.dumps(images), "type": '3',
                          "video_type": item['video_type'], "video_vid": item['video_vid'],
                          "kafka_msg_type": "img_video_cover"}
                # 保存到mysql
                # connector = MysqlUtil()
                # MysqlDao.insert_img_video(connector, params)
                # connector.end()
                # 推送kafka
                WxArticlePrd.send_msg(params)
        return item

    def close_spider(self, spider):
        # spider.logger.debug('--------spider_article_info_3------------end')
        pass

    def push_to_cos(self, local_path, img_info, result_arr: list):
        result = txcosutil.push_wxart_obj_single(local_path)
        img_info['path'] = result['cos_url']
        result_arr.append(result)


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
        if isinstance(item, VideoDownloadItem):
            for file_url in item['file_urls']:
                # 为request带上meta参数，把item传递过去
                yield Request(file_url, meta={'item': item})

    def close_spider(self, spider):
        # spider.logger.debug('--------spider_article_info_4------------end')
        pass


class VideoSavePipeline(object):

    def __init__(self, mongo_uri, mongo_db, mongo_port, server_url):
        # 初始化方法__new__:构造方法，在内存中开辟一块空间
        # self.client = pymongo.MongoClient(mongo_uri, mongo_port)
        # self.db = self.client[mongo_db]
        # self.server_url = server_url
        pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            # mongo_uri=crawler.settings.get('MONGO_URI'),
            # mongo_db=crawler.settings.get('MONGO_DB'),
            # mongo_port=crawler.settings.get('MONGO_PORT'),
            # server_url=crawler.settings.get('SELF_BASE_SERVER_URL')
        )

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        if isinstance(item, VideoDownloadItem) and item['files']:
            video_path = '/video/' + item['files'][0]['path']
            params = {"fakeid": item['fakeid'], "article_id": item['article_id'],
                      "path": video_path, "info": json.dumps(item['files']),
                      "type": '2', "video_type": item['video_type'], "video_vid": item['video_vid'],
                      "kafka_msg_type": "video"}
            # connector = MysqlUtil()
            # MysqlDao.insert_img_video(connector, params)
            # connector.end()
            # 推送kafka
            WxArticlePrd.send_msg(params)
            # MONGO表名为wx_img_video，插入数据
            # self.db['wx_img_video'].insert_one({'fakeid': item['fakeid'], 'article_id': item['article_id'],
            #                                     'path': video_url, 'result': json.dumps(item['files']),
            #                                     'type': '2'})

    def close_spider(self, spider):
        # spider.logger.debug('--------spider_article_info_5------------end')
        pass
