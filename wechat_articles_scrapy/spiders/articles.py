import json
import re


import requests
import scrapy
from bs4 import BeautifulSoup
from bs4.element import Tag
from furl import furl, urllib
from scrapy.utils.project import get_project_settings

from wechat_articles_scrapy.db.Dao import MysqlDao
from wechat_articles_scrapy.items import ImgDownloadItem, ArticleInfoItem, VideoDownloadItem
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
    test_art_link = 'https://mp.weixin.qq.com/s?__biz=MzUzNTAxODAzMA==&mid=2247495057&idx=1&sn=e2fb647752351b88c64068ff64190c7e&ascene=1&devicetype=android-29&version=27001135&nettype=3gnet&abtest_cookie=AAACAA%3D%3D&lang=zh_CN&exportkey=AcoR9GAVn5FHO2zOhibs9XU%3D&pass_ticket=KEKPfD2CWctHtwJJhorDl47%2F7OEwzLeptxToo1UbjBLxSmG07bjijfj1paPaTkbr&wx_header=1'
    test_art_id = '2247495057_1'
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
                yield ai_item
                artresp = requests.get(url=arturl)
                art_html = BeautifulSoup(artresp.content, 'lxml')
                img_arr = art_html.find_all('img')
                img_item = ImgDownloadItem()
                img_item['fakeid'] = ffurl.args['__biz']
                img_item['article_id'] = article_id_temp
                img_item['title'] = art['title']
                img_item['digest'] = art['digest']
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
                soup_html = "html"
                for temp_html in art_html.contents:
                    if isinstance(temp_html, Tag):
                        soup_html = temp_html.prettify()
                        break
                img_item['soup_html'] = soup_html
                img_item['img_poz'] = '0'  # 正文图片
                img_item['video_type'] = ""
                img_item['video_vid'] = ""
                self.logger.debug(f'===============img_url================{image_urls}')
                # 返回图片item
                yield img_item

                # 处理视频
                ifr_arr = art_html.find_all('iframe')
                if ifr_arr:
                    count = 0
                    for ifr in ifr_arr:
                        ifr_attrs = ifr.attrs
                        video_type = ""
                        video_vid = ""
                        # 处理微信视频
                        if 'data-mpvid' in ifr_attrs:
                            # 有data-mpvid说明是微信视频
                            video_type = "1"
                            video_vid = ifr_attrs["data-mpvid"]
                            wx_videourl_url = self.settings['SELF_GETVIDEOURL_URL'].format(ffurl.args['__biz'],
                                                                                           ffurl.args['mid'],
                                                                                           ffurl.args['idx'], video_vid)
                            req_meta = {'article_id': article_id_temp, 'fakeid': ffurl.args['__biz'],
                                        'video_vid': video_vid, 'video_type': video_type, 'count': count}
                            request = scrapy.Request(url=wx_videourl_url, meta=req_meta,
                                                     callback=ArticlesSpider.video_parse)
                            # 返回获取视频url Request
                            yield request
                        else:
                            # 处理其他视频
                            video_html_url = ifr.attrs["data-src"]
                            print("------------Other_video_html_url-------------", video_html_url)
                            if "v.qq.com" in video_html_url:
                                # 腾讯视频
                                video_type = "2"
                                self.logger.info(f'--------tencent_video_html--------{video_html_url}')
                                video_ffurl = furl(video_html_url)
                                video_vid = video_ffurl.args['vid']
                                video_conf_url = self.settings['TENCENT_VIDEO_CONF_URL'].format(video_vid)
                                # 获取腾讯云视频参数
                                self.logger.info(f'--------tencent_video_conf_url--------{video_conf_url}')
                                video_conf_resp = requests.get(url=video_conf_url)
                                # bytes 转 字符串
                                video_conf_str = video_conf_resp.content.decode()
                                video_conf_str = video_conf_str[video_conf_str.index("(") + 1: len(video_conf_str) - 1]
                                video_conf_json = json.loads(video_conf_str)
                                self.logger.info(f'--------tencent_video_conf_resp--------{video_conf_json}')
                                fn = video_conf_json["vl"]["vi"][0]["fn"]
                                fvkey = video_conf_json["vl"]["vi"][0]["fvkey"]
                                ui_list = video_conf_json["vl"]["vi"][0]["ul"]["ui"]
                                video_url = ""
                                # 拼接腾讯云视频链接
                                for ui in ui_list:
                                    if "http://ugc" in ui["url"]:
                                        video_url = ui["url"]
                                        break
                                if video_url != "":
                                    video_url = fn.join([video_url, "?vkey="]).join(["", fvkey])
                                    self.logger.info(f'--------tencent_video_url--------{video_url}')
                                    video_item = VideoDownloadItem()
                                    video_item['fakeid'] = ffurl.args['__biz']
                                    video_item['article_id'] = article_id_temp
                                    video_item['video_type'] = video_type
                                    video_item['video_vid'] = video_vid
                                    video_item['file_urls'] = [video_url]
                                    video_item['count'] = count
                                    yield video_item
                                else:
                                    self.logger.info(f"--------------腾讯云链接获取异常--------------{article_id_temp}")
                        # 处理视频封面
                        if 'data-cover' in ifr_attrs:
                            video_cover_url = ifr_attrs["data-cover"]
                            video_cover_url = urllib.parse.unquote(video_cover_url)
                            print("------------video_cover_url-------------", video_cover_url)
                            video_cover_item = ImgDownloadItem()
                            video_cover_item['fakeid'] = ffurl.args['__biz']
                            video_cover_item['article_id'] = article_id_temp
                            video_cover_item['image_urls'] = [video_cover_url]
                            video_cover_item['img_tag_list'] = []
                            video_cover_item['img_poz'] = "1"
                            video_cover_item['video_type'] = video_type
                            video_cover_item['video_vid'] = video_vid
                            video_cover_item['count'] = count
                            yield video_cover_item
                        count = count + 1
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
                    item = VideoDownloadItem()
                    item['fakeid'] = response.meta['fakeid']
                    item['article_id'] = response.meta['article_id']
                    item['video_type'] = response.meta['video_type']
                    item['video_vid'] = response.meta['video_vid']
                    item['file_urls'] = [url_temp['url']]
                    item['count'] = response.meta['count']
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
            result = re.findall(target, content)
            if result is not None:
                result = {}.fromkeys(result).keys()  # 去重
                self.logger.debug(f'获取vid-------------------------------------------{result}')
                return result
        return None
