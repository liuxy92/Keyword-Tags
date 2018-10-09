# -*- coding: utf-8 -*-
import datetime
import re
import uuid

import scrapy
import time

from video.file_model import File_mod
from video.items import VideoItem
import json
import urllib
from urllib import parse
import subprocess


class HuanqiuSpider(scrapy.Spider):
    name = 'ce_baomihua'
    start_urls = [
        'http://video.baomihua.com/v/37832784'
    ]

    def parse(self, response):
        item = VideoItem()
        now_time = datetime.datetime.now().strftime('%Y%m')
        item['NewsID'] = now_time + '-' + str(uuid.uuid1())
        # item['NewsCategory'] = '001.003.001'
        item['SourceCategory'] = '爆米花视频-搞笑'  # 改为 爆米花+分类

        item['NewsCategory'] = '001.003.021'


        item['NewsType'] = 2
        item['NewsTitle'] = '爆米花视频'
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['SourceName'] = '爆米花视频'  # 改为视频的来源
        item['NewsDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        item['NewsRawUrl'] = response.url

        item['NewsContent'] = None

        # 通过you-get 方法获取到视频的真实地址，--url/-u,--json
        # allurl = subprocess.getstatusoutput('you-get -u {0}'.format(item['NewsRawUrl']))
        allurl = subprocess.getstatusoutput('you-get --json {0}'.format(response.url))
        print('=====================')
        print(allurl)

        if allurl is not None:
            # results = re.findall(r'URLs:(.*)', str(allurl))
            results = json.loads(allurl[1])
            result = results['streams']['__default__']['src'][0]
            # print(results)
            # result = results[0][2:-2]

            # 1.存储视频到本地
            a = File_mod(result)
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

            image_url = response.meta['videoImgUrl']
            item['image_url'] = image_url
            # 1\下载图片
            a = File_mod(image_url)
            full_name_iamge = a.Download_image()
            item['FileDirectory'] = a.detail_fdfs_file(full_name_iamge)
            a.Delete_image(full_name_iamge)

            yield item
