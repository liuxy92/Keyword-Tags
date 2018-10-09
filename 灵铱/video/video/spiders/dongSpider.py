# -*- coding: utf-8 -*-
import datetime
import json
import re
import os
import uuid

import requests
import scrapy
from hashlib import md5

import time

from video.file_model import File_mod
from video.items import VideoItem


class DongspiderSpider(scrapy.Spider):
    name = 'dongSpider'
    allowed_domains = ['eastday.com']
    # start_urls = ['http://eastday.com/']
    baseURL = 'http://videoapi.dftoutiao.com/VideositeView/pcrefresh?param={0}&typeid={1}&num=40&jsonpcallback=jQuery18303655489826988778_1523243989287&_={2}'
    param = "DFTT_VIDEO_PC%09"
    num = 12
    offsets = [i for i in range(0,20)]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",

    }

    typeid = ['700003', '700010', '700008', '700009', '700007', '700006', '700014', '700017', '700013', '700015', '700004']

    def start_requests(self):
        for tid in self.typeid:
            for offset in range:
                yield scrapy.Request(self.baseURL.format(self.param + str(offset), tid, time.time() * 1000), callback=self.parse_index)

    def parse_index(self, response):
        content = response.text
        results = content[content.index('(') + 1:-1]
        res = json.loads(results)

        for result in res['data']:
            title = result['title']
            all_link = 'http://video.eastday.com/a/' + result['htmlname']
            image_url_a = result['llunb'][0]
            image_url_b = image_url_a['src']
            NewsDate = result['vdt']
            # print(NewsDate)
            # print(type(NewsDate))
            yield scrapy.Request(all_link, meta={'title': title, 'image_url_b': image_url_b, 'all_link': all_link, 'NewsDate':NewsDate},callback=self.parse_video)

        # self.offset += 1
        # self.num += 12
        # new_link = self.param + str(self.offset)
        # for tid in self.typeid:
        #     yield scrapy.Request(self.baseURL.format(new_link, tid, str(self.num), time.time() * 1000),
        #                          callback=self.parse_index)

    def parse_video(self, response):
        item = VideoItem()
        item['NewsRawUrl'] = response.meta['all_link']
        now_time = datetime.datetime.now().strftime('%Y%m')
        item['NewsID'] = now_time + '-' + str(uuid.uuid1())

        # item['NewsCategory'] = '001.003.001'
        SourceCategory = response.xpath('//*[@id="player"]/div[2]/div[1]/div[1]/div/a[1]/i/text()').extract_first()

        if SourceCategory == '资讯':
            item['SourceCategory'] = '头条视频-' + SourceCategory

            item['NewsCategory'] = '001.003.001'
        elif SourceCategory == '娱乐':
            item['SourceCategory'] = '头条视频-' + SourceCategory

            item['NewsCategory'] = '001.003.005'
        elif SourceCategory == '科技':
            item['SourceCategory'] = '头条视频-' + SourceCategory

            item['NewsCategory'] = '001.003.006'
        elif SourceCategory == '财经':
            item['SourceCategory'] = '头条视频-' + SourceCategory

            item['NewsCategory'] = '001.003.007'
        elif SourceCategory == '汽车':
            item['SourceCategory'] = '头条视频-' + SourceCategory

            item['NewsCategory'] = '001.003.008'
        elif SourceCategory == '体育':
            item['SourceCategory'] = '头条视频-' + SourceCategory

            item['NewsCategory'] = '001.003.010'
        elif SourceCategory == '时尚':
            item['SourceCategory'] = '头条视频-' + SourceCategory

            item['NewsCategory'] = '001.003.012'
        elif SourceCategory == '游戏':
            item['SourceCategory'] = '头条视频-' + SourceCategory

            item['NewsCategory'] = '001.003.016'
        elif SourceCategory == '旅游':
            item['SourceCategory'] = '头条视频-' + SourceCategory

            item['NewsCategory'] = '001.003.017'
        elif SourceCategory == '亲子':
            item['SourceCategory'] = '头条视频-' + SourceCategory

            item['NewsCategory'] = '001.003.018'
        elif SourceCategory == '纪录片':
            item['SourceCategory'] = '头条视频-' + SourceCategory

            item['NewsCategory'] = '001.003.019'

        item['NewsType'] = 2
        title = response.meta['title']
        item['NewsTitle'] = title
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['SourceName'] = '头条视频'
        NewsDate = response.meta['NewsDate']
        # NewsDate_aft = datetime.datetime.strptime(NewsDate, '%Y-%m-%d %H:%M')

        item['NewsDate'] = NewsDate
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        item['NewsContent'] = None

        pattern = re.compile('var mp4 = "(.*?)"', re.S)
        data = re.search(pattern, response.text).group(1)
        all_link = 'http://mv.eastday.com/' + data[19:]

        # 1.存储视频到本地
        response_url = response.url
        a = File_mod(all_link, response_url)
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

        image_url = response.meta['image_url_b']
        item['image_url'] = image_url
        # 1\下载图片
        a = File_mod(image_url, response_url)
        full_name_iamge = a.Download_image()
        item['FileDirectory'] = a.detail_fdfs_file(full_name_iamge)
        a.Delete_image(full_name_iamge)

        yield item
