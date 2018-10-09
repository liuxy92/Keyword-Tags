# -*- coding: utf-8 -*-
import json

import requests
import scrapy
import os
from hashlib import md5
from decimal import *
# from renren.items import RenrenItem
import time
import uuid
from fdfs_client.client import *

from renren.file_model import File_mod
from renren.items import RenrenItem


class VspiderSpider(scrapy.Spider):
    name = 'vspider'
    # allowed_domains = ['rrmj.tv']
    # start_urls = ['http://web.rr.tv/v3plus/video/categoryIndex']
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        'clientVersion': '0.1.0',
        'clientType': 'web',

    }
    headers2 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    }
    pages = [i for i in range(1, 10)]
    url = 'http://web.rr.tv/v3plus/video/categoryIndex'
    client = Fdfs_client('/etc/fdfs/client.conf')

    cids = ['2', '8', '10']

    def start_requests(self):
        for cid in self.cids:
            for page in self.pages:
                yield scrapy.FormRequest(
                    url=self.url,
                    formdata={"categoryId": cid,"page": str(page)},
                    headers=self.headers,
                    callback=self.parse_page,

                )
    def parse_page(self, response):
        result = json.loads(response.text)
        if not result:
            return None

        aaaa = result['data']['results']
        for item in aaaa:
            id = item['id']
            image = item['cover']
            title = item['title']
            all_link = "http://www.rrmj.tv/#/video/" + str(id)
            # print(str(id) +"   "+all_link + '   ' + image + '  ' + title)
            api_url = 'http://api.rr.tv/v3plus/video/getVideoPlayLinkByVideoId'
            yield scrapy.FormRequest(api_url, meta={'image': image, 'title': title,'all_link': all_link}, formdata={'videoId': str(id)}, headers=self.headers, callback=self.parse_video)
        # self.page += 1
        # for cid in self.cids:
        #     yield scrapy.FormRequest(url=self.url, formdata={"categoryId": cid, "page": str(self.page)}, headers=self.headers, callback=self.parse_page,)

    def parse_video(self, response):
        item = RenrenItem()
        item['NewsRawUrl'] = response.meta['all_link']
        item['NewsID'] = str(uuid.uuid1())
        item['NewsCategory'] = '001.003.001'
        item['SourceCategory'] = response.xpath('//*[@id="crumbsBar"]/div/div[1]/div/a[1]/text()').extract_first()
        item['NewsType'] = 2
        item['NewsTitle'] =response.meta['title']
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['SourceName'] ='人人视频'
        item['NewsDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        item['NewsContent'] = 'None'
        resulta = json.loads(response.text)
        link = resulta['data']['playLink']
        # 1.存储视频到本地
        a = File_mod(link)
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

        image_url = response.meta['image']
        item['image_url'] = image_url
        # 1\下载图片
        a = File_mod(image_url)
        full_name_iamge = a.Download_image()
        item['FileDirectory'] = a.detail_fdfs_file(full_name_iamge)
        a.Delete_image(full_name_iamge)

        yield item





