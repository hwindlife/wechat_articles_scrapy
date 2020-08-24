# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# class WechatArticlesScrapyItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass

class ArticleInfoItem(scrapy.Item):
    # 公众号唯一标识
    fakeid = scrapy.Field()
    # 文章id
    article_id = scrapy.Field()
    # 文章标题
    title = scrapy.Field()
    # 摘要
    digest = scrapy.Field()
    # 链接
    link = scrapy.Field()
    # 封面图链接
    cover_url = scrapy.Field()
    # 微信创建时间
    create_time_wx = scrapy.Field()


class ImgDownloadItem(scrapy.Item):
    # 公众号唯一标识
    fakeid = scrapy.Field()
    # 文章id
    article_id = scrapy.Field()
    # 文章标题
    title = scrapy.Field()
    # 摘要
    digest = scrapy.Field()
    # 图片tag列表
    img_tag_list = scrapy.Field()
    # 页面soup对象
    soup_html = scrapy.Field()
    # 图片种类，1：视频封面
    img_poz = scrapy.Field()
    # 视频类型，1：微信视频，2：腾讯视频，3：没有iframe父标签的视频
    video_type = scrapy.Field()
    # 视频vid
    video_vid = scrapy.Field()
    # 图片URL
    image_urls = scrapy.Field()
    # 图片结果信息
    images = scrapy.Field()
    # 计数字段，封面图片用
    count = scrapy.Field()


class VideoDownloadItem(scrapy.Item):
    # 公众号唯一标识
    fakeid = scrapy.Field()
    # 文章id
    article_id = scrapy.Field()
    # 视频类型，1：微信视频，2：腾讯视频，3：没有iframe父标签的视频
    video_type = scrapy.Field()
    # 视频vid
    video_vid = scrapy.Field()
    # 文件url
    file_urls = scrapy.Field()
    # 文件结果信息
    files = scrapy.Field()
    # 计数字段
    count = scrapy.Field()




