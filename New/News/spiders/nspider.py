# -*- coding: utf-8 -*-
import datetime
import uuid

import scrapy
import execjs
import time
import json

from ..file_model import File_mod
from ..items import NewsItem

from decimal import *
import requests

from hashlib import md5
from fdfs_client.client import *
import os
from urllib.parse import urljoin

import re
from scrapy.selector import Selector

class NspiderSpider(scrapy.Spider):
    name = 'nspider'
    # allowed_domains = ['yidianzixun.com']
    # start_urls = ['http://yidianzixun.com/']
    # url = "http://www.yidianzixun.com/home/q/news_list_for_channel"
    url = 'http://www.yidianzixun.com/home/q/news_list_for_channel?channel_id={0}&cstart={1}&cend={2}&infinite=true&refresh=1&__from__=pc&multi=5&appid=web_yidian'
    params = {
        "channel_id": "12444462422",
        "cstart": "10",
        "cend": "20",
        "infinite": "true",
        "refresh": "1",
        "__from__": "pc",
        "multi": "5",
        "appid": "web_yidian"
    }

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Host": "www.yidianzixun.com",
        "Pragma": "no-cache",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://www.yidianzixun.com/channel/c11",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    cookies = {
        "JSESSIONID": "02376b80c80639539c7b73c9acbd3e60cd73408126f1a2ce8e0e67d3f2f28f74",
        # "JSESSIONID": "8623960155d1535a7e0d4ce21adf77cf5c704f053032b0bcecbcff0348bcc680",

        # 02376b80c80639539c7b73c9acbd3e60cd73408126f1a2ce8e0e67d3f2f28f74
        #02376b80c80639539c7b73c9acbd3e60cd73408126f1a2ce8e0e67d3f2f28f74
        "wuid": "289895602574831",
        "wuid_createAt": "2018-04-16 15:51:19",
        "weather_auth": "2",
        "Hm_lvt_15fafbae2b9b11d280c79eff3b840e45": "1523865079",
        "UM_distinctid": "162cd6fd0c7ac9-02d7cb015c9144-3b7c015b-1fa400-162cd6fd0c8f9b",
        "CNZZDATA1255169715": "268439245-1523861655-%7C1523861655",
        "Hm_lpvt_15fafbae2b9b11d280c79eff3b840e45": "1523865295",
        "captcha": "s%3A059f3736ab053acaf973b50ce3fd509d.IDh1%2FtV8lF0oxw2LfyCZldtNxVcwsddKix3vlz3E3jw",
        "cn_1255169715_dplus": "%7B%22distinct_id%22%3A%20%22162cd6fd0c7ac9-02d7cb015c9144-3b7c015b-1fa400-162cd6fd0c8f9b%22%2C%22sp%22%3A%20%7B%22%24_sessionid%22%3A%200%2C%22%24_sessionTime%22%3A%201523865294%2C%22%24dp%22%3A%200%2C%22%24_sessionPVTime%22%3A%201523865294%7D%7D",
        "sptoken": "U%3B%3B%3D%3E99%3C%3F%3F28U%3B%3AU8%3AU48261efeced332cc9f20413132c69381e96e4aafcc39a24366a39c806f2d8efa",
    }
    # 通过exscjs解析js
    ctx = execjs.compile("""
         function test(n, e, i) {
                t = "U;;=>99<??28U;:U8:U48261efeced332cc9f20413132c69381e96e4aafcc39a24366a39c806f2d8efa"
                e = e || 0,
                i = i || 10;
                for (var o = "_" + n + "_" + e + "_" + i + "_", a = "", c = 0; c < o.length; c++) {
                    var r = 10 ^ o.charCodeAt(c);
                    a += String.fromCharCode(r)
                }
                t = /^U.+?U.{1,3}U.{1,3}U/.test(t) ? t.replace(/^U.+?U.{1,3}U.{1,3}U/, a) : a + t,
                co = "sptoken=" + encodeURIComponent(t) + ";domain=.yidianzixun.com;path=/;max-age=2592000"
                co1 = encodeURIComponent(t)
                return co1;
            }
         """)
   # 20391812518 新时代（没有）
    #22692507381 汽车
    # 22692507221娱乐
    # 22692507237军事
    # 22692507253 体育
    # 22692507285 财经
    # 22692507301 科技
    # channel_id = ['12444462582', '12444462438', '12444462454', '12444462486', '22101121286', '12444462838', "12444462422"]
    channel_id = ["12444462582"]

    def start_requests(self):
        for cid in self.channel_id:
            for page in range(1, 2):
                start_page = (page - 1) * 10
                end_page = page * 10
                self.cookies["sptoken"] = self.ctx.call("test", cid, start_page, end_page)

                yield scrapy.Request(self.url.format(cid, start_page, end_page), headers=self.headers, cookies=self.cookies, callback=self.parse_page)

    def parse_page(self, response):
        # print(response.text)
        if response:
            result = json.loads(response.text)
            # print(result)
            # print('======================')
            # print(response.url)
            response_url = response.url
            for i in result["result"]:
                date = i['date']
                title = i['title']
                url = i['url']
                source = i['source']
                # category = i['category']
                # print(date)
                # print(title)
                # print(url)
                # print(source)
                # print(category)
                yield scrapy.Request(url, meta={'date': date, 'title': title, 'url': url, 'source': source, 'response_url': response_url}, callback=self.parse_page_detaile)

    def parse_page_detaile(self, response):
        item = NewsItem()

        now_time = datetime.datetime.now().strftime('%Y%m')
        item['NewsID'] = now_time + '-' + str(uuid.uuid1())
        response_url = response.meta['response_url']
        if '12444462422' in response_url:
            item['SourceCategory'] = '一点资讯-' + '娱乐'
            item['NewsCategory'] = '001.005'
        elif '12444462582' in response_url:
            item['SourceCategory'] = '一点资讯-' + '汽车'
            item['NewsCategory'] = '001.008'
        elif '12444462438' in response_url:
            item['SourceCategory'] = '一点资讯-' + '军事'
            item['NewsCategory'] = '001.011'
        elif '12444462454' in response_url:
            item['SourceCategory'] = '一点资讯-' + '体育'
            item['NewsCategory'] = '001.010'
        elif '12444462486' in response_url:
            item['SourceCategory'] = '一点资讯-' + '财经'
            item['NewsCategory'] = '001.007'
        elif '22101121286' in response_url:
            item['SourceCategory'] = '一点资讯-' + '游戏'
            item['NewsCategory'] = '001.016'
        elif '12444462838' in response_url:
            item['SourceCategory'] = '一点资讯-' + '数码'
            item['NewsCategory'] = '001.024'
        # elif '12444462550' in response_url:
        #     item['SourceCategory'] = '一点资讯-' + '养生'
        #     item['NewsCategory'] = '001.014'
        # elif '22692507381' in response_url:
        #     item['SourceCategory'] = '一点资讯-' + '汽车'
        #     item['NewsCategory'] = '001.008'
        # elif '20391812518' in response_url:
        #     item['SourceCategory'] = '一点资讯-' + '头条'
        #     item['NewsCategory'] = '001.001'
        # elif '12444462502' in response_url:
        #     item['SourceCategory'] = '一点资讯-' + '科技'
        #     item['NewsCategory'] = '001.006'


        item['NewsType'] = 0

        Newstitle = response.meta['title']

        item['NewsTitle'] = Newstitle

        item['NewsRawUrl'] = response.meta['url']
        SourceName = response.meta['source']

        item['SourceName'] = SourceName
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        Newstime = response.meta['date']
        # NewsDate = datetime.datetime.strptime(Newstime, '%Y-%m-%d %H:%M:%S')
        item['NewsDate'] = Newstime

        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0

        image_urls = response.xpath("//div[@class='content-bd']/p/span/img/@src | //div[@class='yidian-content']/p/span/img/@src | //div[@class='news_part']/div/img/@src | //div[@class='imedia-article']/p/span/img/@src | //div[@class='yidian-content']/p/img/@src | //div[@class='content-bd']/div//span/img/@src | //div[@class='yidian-content']/p/img/@alt_src | //div[@class='img-holder']/img/@src | //div[@class='article long-article']/p/img/@src | //div[@id='yidian-content']/p/span/img/@src | //div[@class='com-insert-images']/figure/img/@src | //div[@class='contentDetailed']/p/img/@src | //div[@class='video-wrapper']/video/@src | //span[@class='a-image']/img/@src | //div[@class='ina_content ']/p/a/img/@src | //div[@id='showall233']/p/img/@src").extract()
        content = ''.join(response.xpath("//div[@class='content-bd']/p | //div[@class='yidian-content']/p | //div[@class='preview-topic-summary']/div | //div[@class='news_part']/text() | //div[@id='p-detail']/p | //div[@class='article long-article']/p | //div[@class='contentDetailed']/p | //div[@class='video-wrapper']/video/@src | //div[@id='imedia-article']/section/section/section/section/p | //div[@class='ina_content ']/p | //div[@id='showall233']/p | //div[@class='imedia-article']/p").extract())
        # //div[@class='imedia-article']/p 文章链接http://www.yidianzixun.com/article/0JDrFqoZ
        # result = re.sub(r'div', 'p', response.text)
        # content = ''.join(Selector(text=result).xpath("//div[@class='content-bd']/p | //div[@class='yidian-content']/p | //div[@class='imedia-article']/p | //div[@class='preview-topic-summary']/div | //div[@class='news_part']/text() | //div[@id='p-detail']/p | //div[@class='article long-article']/p | //div[@class='contentDetailed']/p | //div[@class='video-wrapper']/video/@src | //div[@id='imedia-article']/section/section/section/section/p").extract())

        listFiles = []
        if image_urls or content:
            for image_url in image_urls:
                response_url = response.url
                a = File_mod(image_url, content, response_url)
                content = a.detail_file()
                if image_url.endswith('mp4'):
                    full_name = a.Download_video()
                    filemodel = {}
                    filemodel['FileID'] = str(uuid.uuid1())
                    filemodel['FileType'] = 0
                    filemodel['FileDirectory'] = a.detail_fdfs_file(full_name)
                    filemodel['FileDirectoryCompress'] = a.detail_fdfs_file(full_name)
                    filemodel['FileDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    filemodel['FileLength'] = a.detail_FileLength(full_name)
                    filemodel['FileUserID'] = None
                    filemodel['Description'] = None
                    filemodel['NewsID'] = item['NewsID']
                    filemodel['image_url'] = image_url
                    listFiles.append(filemodel)
                    a.Delete_image(full_name)
                else:
                    full_name = a.Download_image()
                    filemodel = {}
                    filemodel['FileID'] = str(uuid.uuid1())
                    filemodel['FileType'] = 0
                    filemodel['FileDirectory'] = a.detail_fdfs_file(full_name)
                    filemodel['FileDirectoryCompress'] = a.detail_fdfs_file(full_name)
                    filemodel['FileDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    filemodel['FileLength'] = a.detail_FileLength(full_name)
                    filemodel['FileUserID'] = None
                    filemodel['Description'] = None
                    filemodel['NewsID'] = item['NewsID']
                    filemodel['image_url'] = image_url
                    listFiles.append(filemodel)
                    a.Delete_image(full_name)

        item['NewsContent'] = content
        item['FileList'] = listFiles

        yield item
