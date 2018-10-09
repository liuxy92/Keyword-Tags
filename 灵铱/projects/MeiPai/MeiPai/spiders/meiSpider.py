# -*- coding: utf-8 -*-
import json
import uuid

import scrapy
import time
from pyquery import PyQuery as pq
import requests
from MeiPai.file_model import File_mod
from MeiPai.items import MeipaiItem
# from jie_mi_bs import decode
import os
from hashlib import md5
from MeiPai.jie_mi_bs import decode
class MeispiderSpider(scrapy.Spider):
    name = 'meiSpider'
    allowed_domains = ['meipai.com']
    start_urls = ['http://www.meipai.com/medias/hot']
    baseURL = 'http://www.meipai.com/topics/news_timeline?page={0}&count=24&tid={1}'
    pages = [i for i in range(1, 10)]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    }
    # urls = ['http://www.meipai.com/topics/news_timeline?page=1&count=24&tid=5872639793429995335',
    #         'http://www.meipai.com/topics/news_timeline?page=1&count=24&tid=5879621667768487138'
    #         ]
    tids = ['5872639793429995335', '5879621667768487138']

    def start_requests(self):
        for tid in self.tids:
            for page in self.pages:
                yield scrapy.Request(self.baseURL.format(page, tid), callback=self.parse_index)
            # yield scrapy.Request("http://www.meipai.com/home/hot_timeline?page=1&count=12", callback=self.parse_index)

    def parse_index(self, response):
        results = json.loads(response.text)
        if not results:
            return None
        for item in results['medias']:
            id = item.get("id")
            image_url = item.get('cover_pic')
            title = item.get('caption_complete')
            video_url = item.get('url')

            if 'live' not in video_url:
                yield scrapy.Request(video_url, meta={'image_url': image_url, 'title': title, 'video_url': video_url},
                                     callback=self.parse_video, headers=self.headers)
    def parse_video(self, response):
        item = MeipaiItem()
        item['NewsRawUrl'] = response.meta['video_url']
        item['NewsID'] = str(uuid.uuid1())
        try:
            SourceCategory = response.xpath('/html/body/div[3]/div[1]/a[2]/text()').extract_first()
            item['SourceCategory'] = SourceCategory.strip()

            if item['SourceCategory'] == '运动':
                item['NewsCategory'] = '001.003.010'
            elif item['SourceCategory'] == '游戏':
                item['NewsCategory'] = '001.003.016'
        except:
            item['SourceCategory'] = None
            item['NewsCategory'] = None

        item['NewsType'] = 2
        title = response.meta['title']
        item['NewsTitle'] = title
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['SourceName'] = '美拍'
        item['NewsDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        item['NewsContent'] = 'None'

        image_url = response.meta['image_url']
        d = pq(response.text)
        downloaded_links_bef = d('meta[property="og:video:url"]').attr('content')
        if downloaded_links_bef:
            downloaded_links = decode(downloaded_links_bef)
        # 1.存储视频到本地
            a = File_mod(downloaded_links)
            full_name_video = a.Download_video()
            item['FileID'] = str(uuid.uuid1())
            item['FileType'] = 0
            item['FileDirectoryCompress'] = a.detail_fdfs_file(full_name_video)
            item['FileDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item['FileLength'] = a.detail_FileLength(full_name_video)
            item['FileUserID'] = None
            item['Description'] = None
            item['NewsID'] = item['NewsID']
            a.Delete_image(full_name_video)
            item['image_url'] = image_url
            # 1\下载图片
            a = File_mod(image_url)
            full_name_iamge = a.Download_image()
            item['FileDirectory'] = a.detail_fdfs_file(full_name_iamge)
            a.Delete_image(full_name_iamge)

            yield item
