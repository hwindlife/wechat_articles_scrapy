import datetime

# Scrapy settings for wechat_articles_scrapy project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'wechat_articles_scrapy'

SPIDER_MODULES = ['wechat_articles_scrapy.spiders']
NEWSPIDER_MODULE = 'wechat_articles_scrapy.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'wechat_articles_scrapy (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'wechat_articles_scrapy.middlewares.WechatArticlesScrapySpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'wechat_articles_scrapy.middlewares.WechatArticlesScrapyDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'wechat_articles_scrapy.pipelines.WechatArticlesScrapyPipeline': 300,
# }

ITEM_PIPELINES = {
    # 'scrapy.pipelines.files.FilesPipeline': 1
    'wechat_articles_scrapy.pipelines.ArticleInfoPipeline': 300,
    'wechat_articles_scrapy.pipelines.ImagePipeline': 301,
    'wechat_articles_scrapy.pipelines.ImageSavePipeline': 302,
    'wechat_articles_scrapy.pipelines.VideoDownloadPipeline': 303,
    'wechat_articles_scrapy.pipelines.VideoSavePipeline': 304,
    # 'scrapy.pipelines.images.ImagesPipeline': 1
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# 保存文件设置
IMAGES_STORE = 'D:\\develop\\temp\\scrapy\\wechat\\images'
IMAGES_URLS_FIELD = 'image_urls'
IMAGES_RESULT_FIELD = 'images'
# IMAGES_THUMBS = {
#     'small': (80, 80),
#     'big': (300, 300)
# }

# 保存文件设置
FILES_STORE = 'D:\\develop\\temp\\scrapy\\wechat\\video'
FILES_URLS_FIELD = 'file_urls'
FILES_RESULT_FIELD = 'files'

# MONGO配置
MONGO_URI = 'localhost'
MONGO_DB = 'scrapy'
MONGO_PORT = 27017

# mysql配置
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_DATABASE = 'scrapy'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_CHARSET = 'utf8'

# 日志配置
startDate = datetime.datetime.now().strftime('%Y-%m-%d')
LOG_FILE = f"log/article.{startDate}.log"
LOG_LEVEL = 'DEBUG'
# 启用logging，默认True
LOG_ENABLED = True
# 默认: ‘utf-8’，logging使用的编码
LOG_ENCODING = 'utf-8'

# ================自定义配置================
# 服务器根链接
SELF_BASE_SERVER_URL = 'http://www.example.com/'
# 获取微信视频url列表链接
SELF_GETVIDEOURL_URL = 'https://mp.weixin.qq.com/mp/videoplayer?action=get_mp_video_play_url&preview=0&__biz={}&mid={}&idx={}&vid={}&uin=&key=&pass_ticket=&wxtoken=777&devicetype=&appmsg_token=&x5=0&f=json'
# 获取公众号列表接口链接
SELF_OFFICIAL_URL = 'https://mp.weixin.qq.com/cgi-bin/searchbiz?lang=zh_CN&f=json&action=search_biz&ajax=1&begin={}&count={}&token={}&query={}'
# 获取文章列表接口链接
SELF_ARTICALS_URL = 'https://mp.weixin.qq.com/cgi-bin/appmsg?lang=zh_CN&f=json&action=list_ex&type=9&query=&begin={}&count={}&token={}&fakeid={}'

