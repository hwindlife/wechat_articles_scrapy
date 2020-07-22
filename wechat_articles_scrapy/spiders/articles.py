import json
import re

import requests
import scrapy
from bs4 import BeautifulSoup
from bs4.element import Tag
from furl import furl
from scrapy.utils.project import get_project_settings

from wechat_articles_scrapy.db.Dao import MysqlDao
from wechat_articles_scrapy.items import ImgDownloadItem, ArticleInfoItem, videoDownloadItem
from wechat_articles_scrapy.util.DateUtil import DateUtil


class ArticlesSpider(scrapy.Spider):
    settings = get_project_settings()
    name = 'articles'
    allowed_domains = ['mp.weixin.qq.com']
    start_urls = []

    wx_config = MysqlDao.get_wxconfig()
    fakeid_cls = wx_config[1]
    token = wx_config[2]
    cookie = wx_config[3]
    user_agent = wx_config[4]

    query_info = '泰康之家'
    page_start = '0'
    page_length = '5'

    # 测试模式
    testMode = True
    test_art_link = 'https://mp.weixin.qq.com/s?__biz=MzA4MTM1NDcxMA==&mid=2650376956&idx=1&sn=64749e57c1b684e70b1f26fbd6f98e29&chksm=879b6045b0ece953ad3dd7316edbb0cd6f263fd2286c770b0a216ac69771e21b0553f2b4cb48&mpshare=1&srcid=07222eBRlFfXoIfgzT46fVTt&sharer_sharetime=1595407653440&sharer_shareid=40bf552b62a64ccd008e389d94cc5e23&from=singlemessage&scene=1&subscene=10000&clicktime=1595415668&enterid=1595415668&ascene=1&devicetype=android-29&version=2700103f&nettype=3gnet&abtest_cookie=AAACAA%3D%3D&lang=zh_CN&exportkey=AYDHuJe1szBZMU3Am%2Boh4co%3D&pass_ticket=qM9j5N%2FkGqF8ijxXHxYb8rdp6%2B%2Bavh7hOwu1KabhxBmhCghgHL7H3S4cwJYM%2BL8b&wx_header=1'
    test_art_id = '2650376956_1'
    test_art_artjson = '{"app_msg_list":[{"aid":"","title":"test","digest":"","link":"","cover":"","create_time":1593682407,"link":""}]}'

    # 使用FormRequests发送请求，指定url，请求头信息，cookies
    def start_requests(self):
        if ArticlesSpider.fakeid_cls == '':
            # 获取公众号信息url
            official_url = ArticlesSpider.settings['SELF_OFFICIAL_URL'].format(ArticlesSpider.page_start,
                                                                               ArticlesSpider.page_length,
                                                                               ArticlesSpider.token,
                                                                               ArticlesSpider.query_info)
            yield scrapy.Request(official_url,
                                 headers={"User-Agent": self.user_agent, "cookie": self.cookie},
                                 callback=self.parse)
        else:
            if self.testMode:
                self.logger.debug('---------------test Mode-----------------')
                yield scrapy.Request('https://www.baidu.com',
                                     headers={"User-Agent": self.user_agent, "cookie": self.cookie},
                                     callback=self.articles_parse)
            else:
                # 获取文章列表url
                articals_url = ArticlesSpider.settings['SELF_ARTICALS_URL'].format(ArticlesSpider.page_start,
                                                                                   ArticlesSpider.page_length,
                                                                                   ArticlesSpider.token,
                                                                                   ArticlesSpider.fakeid_cls)
                yield scrapy.Request(articals_url,
                                     headers={"User-Agent": self.user_agent, "cookie": self.cookie},
                                     callback=self.articles_parse)

    def parse(self, response):
        official_info = response.json()['list']
        self.logger.info(f'------------公众号list-----------{official_info}')
        # 获取文章列表url
        articals_url = ArticlesSpider.settings['SELF_ARTICALS_URL'].format(ArticlesSpider.page_start,
                                                                           ArticlesSpider.page_length,
                                                                           ArticlesSpider.token,
                                                                           official_info[0]["fakeid"])
        self.logger.info(f'---------文章列表url----------{articals_url}')
        yield scrapy.Request(articals_url, headers={"User-Agent": self.user_agent, "cookie": self.cookie},
                             callback=self.articles_parse)

    def articles_parse(self, response):
        self.logger.info(
            f'------------文章列表-----------{response.json() if not self.testMode else self.test_art_artjson}')
        artcle_dict = json.loads(response.text if not self.testMode else self.test_art_artjson)
        if 'app_msg_list' in artcle_dict:
            article_list = artcle_dict['app_msg_list']
            for art in article_list:
                article_id_temp = art['aid'] if not self.testMode else self.test_art_id
                # 解析链接，获取参数
                arturl = art['link'] if not self.testMode else self.test_art_link
                ffurl = furl(arturl)
                count = MysqlDao.get_count_by_articleid(article_id_temp)
                if count > 0:
                    self.logger.info(f'-----------article__exist---------------{article_id_temp}')
                    continue
                ai_item = ArticleInfoItem()
                ai_item['fakeid'] = ffurl.args['__biz']
                ai_item['article_id'] = article_id_temp
                ai_item['title'] = art['title']
                ai_item['digest'] = art['digest']
                ai_item['link'] = art['link']
                ai_item['cover_url'] = art['cover']
                ai_item['create_time_wx'] = DateUtil.secondsToDatetime(art['create_time'])
                # 返回文章item
                # yield ai_item
                artresp = requests.get(url=arturl)
                art_html = BeautifulSoup(artresp.content, 'lxml')
                img_arr = art_html.find_all('img')
                img_item = ImgDownloadItem()
                img_item['fakeid'] = ffurl.args['__biz']
                img_item['article_id'] = article_id_temp
                image_urls = []
                img_tag_list = []
                for imgtag in img_arr:
                    imgurl = ArticlesSpider.get_imgurl_wx(imgtag)
                    if imgurl != '' and not imgurl.endswith('svg'):
                        imgurl = "".join(['https:', imgurl]) if imgurl.startswith('//') else imgurl
                        img_tag_list.append(imgtag)
                        image_urls.append(imgurl)
                img_item['image_urls'] = image_urls
                img_item['img_tag_list'] = img_tag_list
                img_item['soup_html'] = art_html
                self.logger.debug(f'===============img_url================{image_urls}')
                # 返回下载图片item
                # yield img_item
                vid = self.get_vid(str(artresp.content), article_id_temp)
                # 没有vid说明没有视频
                if vid is not None:
                    request = scrapy.Request(
                        url=self.settings['SELF_GETVIDEOURL_URL'].format(ffurl.args['__biz'], ffurl.args['mid'],
                                                                         ffurl.args['idx'], vid),
                        meta={'article_id': article_id_temp, 'fakeid': ffurl.args['__biz']},
                        callback=ArticlesSpider.video_parse)
                    # 返回获取视频url Request
                    yield request
                else:
                    ifr_arr = art_html.find_all('iframe')
                    video_html_url = ifr_arr[0].attrs["data-src"]
                    print('--------video_html--------', video_html_url)
                    video_ffurl = furl(video_html_url)
                    tencent_vid = video_ffurl.args['vid']
                    print('--------tencent_vid--------', tencent_vid)
                    video_conf_url = "https://h5vv.video.qq.com/getinfo?callback=tvp_request_getinfo_callback_615764&otype=json&vids={}&platform=11001&sphls=0&sb=1&nocache=0&appVer=V2.0Build9502&vids=e31174xgw73&defaultfmt=auto&sdtfrom=v3010&callback=tvp_request_getinfo_callback_615764"
                    video_conf_url = video_conf_url.format(tencent_vid)
                    print('--------video_conf_url--------', video_conf_url)
                    video_conf_resp = requests.get(url=video_conf_url)
                    video_conf_str = video_conf_resp.content.decode()
                    video_conf_str = video_conf_str[video_conf_str.index("(") + 1: len(video_conf_str) - 1]
                    video_conf_json = json.loads(video_conf_str)
                    print('--------video_conf_resp--------', video_conf_json)
                    fn = video_conf_json["vl"]["vi"][0]["fn"]
                    fvkey = video_conf_json["vl"]["vi"][0]["fvkey"]
                    ui_list = video_conf_json["vl"]["vi"][0]["ul"]["ui"]
                    video_url = ""
                    for ui in ui_list:
                        if "ugcbsy.qq.com" in ui["url"]:
                            video_url = ui["url"]
                    video_url = fn.join([video_url, "?vkey="]).join(["", fvkey])
                    print(video_url)
                    video_item = videoDownloadItem()
                    video_item['fakeid'] = ffurl.args['__biz']
                    video_item['article_id'] = article_id_temp
                    video_item['file_urls'] = [video_url]
                    yield video_item
                if self.testMode:
                    break
        else:
            self.logger.info('获取文章列表失败！')

    @staticmethod
    def video_parse(response):
        if 'url_info' in response.json():
            url_list = response.json()['url_info']
            for url_temp in url_list:
                # 视频质量，1：流程，2：高清，3：超清
                if url_temp['video_quality_level'] == 1:
                    item = videoDownloadItem()
                    item['fakeid'] = response.meta['fakeid']
                    item['article_id'] = response.meta['article_id']
                    item['file_urls'] = [url_temp['url']]
                    yield item
                    break

    @staticmethod
    def get_imgurl_wx(img_tag: Tag):
        url = ''
        attrs = img_tag.attrs
        # print('--------attrs--------', attrs)
        if 'data-src' in attrs:
            url = attrs['data-src']
        elif 'src' in attrs:
            url = attrs['src']
        return url

    def get_vid(self, content, article_id):
        if content is not None and content != '':
            target = r"wxv_.{19}"  # 匹配:wxv_1105179750743556096
            result = re.search(target, content)
            self.logger.info(f"wxv----------artid----------{article_id}-----------result: {result}")
            if result is not None:
                vid = result.group(0)
                self.logger.debug(f'获取vid-------------------------------------------{vid}')
                return vid
        return None
