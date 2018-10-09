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

from video.file_model import File_mod
from video.items import VideoItem


class RenSpider(scrapy.Spider):
    name = 'ren'
    # allowed_domains = ['rrmj.tv']
    # start_urls = ['http://rrmj.tv/']

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
    detail_url = 'http://web.rr.tv/v3plus/video/detail'
    api_url = 'http://api.rr.tv/v3plus/video/getVideoPlayLinkByVideoId'

    client = Fdfs_client('/etc/fdfs/client.conf')

    cids = ['2', '8', '10', '11']  #2娱乐、8科技、10体育、11是纪录片、

    def start_requests(self):
        for cid in self.cids:
            for page in self.pages:
                yield scrapy.FormRequest(
                    url=self.url,
                    formdata={"categoryId": cid,"page": str(page)},
                    headers=self.headers,
                    callback=self.get_page,

                )

    def get_page(self, response):
        result = json.loads(response.text)
        if not result:
            return None

        aaaa = result['data']['results']
        for item in aaaa:
            tcid = item['id']
            # image = item['cover']
            # title = item['title']
            # all_link = "http://www.rrmj.tv/#/video/" + str(tcid)

            yield scrapy.FormRequest(url=self.detail_url, formdata={"videoId": str(tcid)}, headers=self.headers, callback=self.get_page_detail)


    def get_page_detail(self, response):
        res = json.loads(response.text)
        title = res['data']['videoDetailView']['title']
        image = res['data']['videoDetailView']['cover']
        categoryId = res['data']['videoDetailView']['videoCategory']['categoryId']
        videoId = res['data']['videoDetailView']['videoCategory']['videoId']
        all_link = "http://www.rrmj.tv/#/video/" + str(videoId)

        yield scrapy.FormRequest(url=self.api_url, meta={'title': title, 'image': image, 'categoryId': categoryId, 'all_link': all_link}, formdata={'videoId': str(videoId)}, headers=self.headers, callback=self.parse_video)

    def parse_video(self, response):

        print(response.text)
        item = VideoItem()
        item['NewsRawUrl'] = response.meta['all_link']
        now_time = datetime.datetime.now().strftime('%Y%m')
        item['NewsID'] = now_time + '-' + str(uuid.uuid1())
        categoryId = response.meta['categoryId']
        if categoryId == 2:
            item['SourceCategory'] = '人人视频-' + '娱乐'

            item['NewsCategory'] = '001.003.005'
        elif categoryId == 8:
            item['SourceCategory'] = '人人视频-' + '科技'

            item['NewsCategory'] = '001.003.006'
        elif categoryId == 10:
            item['SourceCategory'] = '人人视频-' + '体育'

            item['NewsCategory'] = '001.003.010'
        elif categoryId == 11:
            item['SourceCategory'] = '人人视频-' + '探索'

            item['NewsCategory'] = '001.003.013'

        item['NewsType'] = 2
        item['NewsTitle'] =response.meta['title']
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['SourceName'] = '人人视频'
        item['NewsDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        item['NewsContent'] = 'None'
        resulta = json.loads(response.text)
        link = resulta['data']['playLink']
        # 1.存储视频到本地
        response_url  = response.url
        a = File_mod(link, response_url)
        full_name_video = a.Download_video()

        item['FileID'] = str(uuid.uuid1())
        item['FileType'] = 2

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
        a = File_mod(image_url, response_url)
        full_name_iamge = a.Download_image()
        item['FileDirectory'] = a.detail_fdfs_file(full_name_iamge)
        a.Delete_image(full_name_iamge)

        yield item

