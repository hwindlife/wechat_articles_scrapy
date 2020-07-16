# 文件timerStartDaily.py
import datetime
import os
import shutil
import time

from scrapy import cmdline
# from scrapy import log, signals
# from scrapy.crawler import Crawler as ScrapyCrawler
# from scrapy.utils.project import get_project_settings
# from scrapy.xlib.pydispatch import dispatcher
# from twisted.internet import reactor
#
#
# def scrapy_crawl(name):
#     def stop_reactor():
#         reactor.stop()
#
#     dispatcher.connect(stop_reactor, signal=signals.spider_closed)
#     scrapy_settings = get_project_settings()
#     crawler = ScrapyCrawler(scrapy_settings)
#     crawler.configure()
#     spider = crawler.spiders.create(name)
#     crawler.crawl(spider)
#     crawler.start()
#     log.start()
#     reactor.run()


recoderDir = r"crawls"  # 这是为了爬虫能够续爬而创建的目录，存储续爬需要的数据
checkFile = "isRunning.txt"  # 爬虫是否在运行的标志

startTime = datetime.datetime.now()
print(f"startTime = {startTime}")

i = 0
miniter = 0
while True:
    isRunning = os.path.isfile(checkFile)
    if not isRunning:  # 爬虫不在执行，开始启动爬虫
        # 在爬虫启动之前处理一些事情，清掉JOBDIR = crawls
        isExsit = os.path.isdir(recoderDir)  # 检查JOBDIR目录crawls是否存在
        print(f"articles not running, ready to start. isExsit:{isExsit}")
        if isExsit:
            shutil.rmtree(recoderDir)  # 删除续爬目录crawls及目录下所有文件
            print(f"At time:{datetime.datetime.now()}, delete res:{recoderDir}")
        else:
            print(f"At time:{datetime.datetime.now()}, Dir:{recoderDir} is not exsit.")
        time.sleep(20)
        clawerTime = datetime.datetime.now()
        waitTime = clawerTime - startTime
        print(f"At time:{clawerTime}, start clawer: articles !!!, waitTime:{waitTime}")
        cmdline.execute('scrapy crawl articles -s JOBDIR=crawls/storeMyRequest'.split())
        os.system('scrapy crawl articles -s JOBDIR=crawls/storeMyRequest')
        print('------------爬虫结束了---------------')
        # break  # 爬虫结束之后，退出脚本
    else:
        print(f"At time:{datetime.datetime.now()}, articles is running, sleep to wait.")
    i += 1
    time.sleep(0)  # 每60秒爬取一次
    # miniter += 10
    # if miniter >= 1440:  # 等待满24小时，自动退出监控脚本
    #     break
