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

from dongfang.file_model import File_mod
from dongfang.items import DongfangItem


class DongspiderSpider(scrapy.Spider):
    name = 'dongSpider'
    allowed_domains = ['eastday.com']
    # start_urls = ['http://eastday.com/']
    baseURL = 'http://videoapi.dftoutiao.com/VideositeView/pcrefresh?param={0}&typeid={1}&num=12&jsonpcallback=jQuery18303655489826988778_1523243989287&_={2}'
    param = "DFTT_VIDEO_PC%09"
    num = 12
    offsets = [i for i in range(0,20)]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",

    }

    typeid = ['700003', '700010', '700008', '700009', '700007', '700006', '700014', '700017', '700013', '700015']
    # urls = [
    #     'http://videoapi.dftoutiao.com/VideositeView/pcrefresh?param=baiducom%0915232378134117607%09toutiao_video_pc%09DFTT_VIDEO_PC%091&typeid=700003&num=36&jsonpcallback=jQuery1830298130918181297_1523429555747&_=1523429556063',
    #     'http://videoapi.dftoutiao.com/VideositeView/pcrefresh?param=baiducom%0915232378134117607%09toutiao_video_pc%09DFTT_VIDEO_PC%091&typeid=700010&num=36&jsonpcallback=jQuery183011394122070786117_1523429851950&_=1523429852382',
    #     'http://videoapi.dftoutiao.com/VideositeView/pcrefresh?param=baiducom%0915232378134117607%09toutiao_video_pc%09DFTT_VIDEO_PC%091&typeid=700008&num=36&jsonpcallback=jQuery18304148037238960851_1523429992872&_=1523429993270',
    #     'http://videoapi.dftoutiao.com/VideositeView/pcrefresh?param=baiducom%0915232378134117607%09toutiao_video_pc%09DFTT_VIDEO_PC%091&typeid=700009&num=36&jsonpcallback=jQuery183042632879974604654_1523432192801&_=1523432193247',
    #     'http://videoapi.dftoutiao.com/VideositeView/pcrefresh?param=baiducom%0915232378134117607%09toutiao_video_pc%09DFTT_VIDEO_PC%091&typeid=700007&num=36&jsonpcallback=jQuery18306185858074388231_1523432436484&_=1523432436934',
    #     'http://videoapi.dftoutiao.com/VideositeView/pcrefresh?param=baiducom%0915232378134117607%09toutiao_video_pc%09DFTT_VIDEO_PC%091&typeid=700006&num=36&jsonpcallback=jQuery18306123968547523795_1523432515071&_=1523432515494',
    #     'http://videoapi.dftoutiao.com/VideositeView/pcrefresh?param=baiducom%0915232378134117607%09toutiao_video_pc%09DFTT_VIDEO_PC%091&typeid=700014&num=36&jsonpcallback=jQuery18308802747096570589_1523432643405&_=1523432643766',
    #     'http://videoapi.dftoutiao.com/VideositeView/pcrefresh?param=baiducom%0915232378134117607%09toutiao_video_pc%09DFTT_VIDEO_PC%091&typeid=700017&num=36&jsonpcallback=jQuery18306481612881453871_1523432715035&_=1523432715416',
    #     'http://videoapi.dftoutiao.com/VideositeView/pcrefresh?param=baiducom%0915232378134117607%09toutiao_video_pc%09DFTT_VIDEO_PC%091&typeid=700013&num=36&jsonpcallback=jQuery18309017251938050981_1523432787991&_=1523432788352',
    #     'http://videoapi.dftoutiao.com/VideositeView/pcrefresh?param=baiducom%0915232378134117607%09toutiao_video_pc%09DFTT_VIDEO_PC%091&typeid=700015&num=36&jsonpcallback=jQuery18307826724338917108_1523432846823&_=1523432847177'
    # ]

    def start_requests(self):
        for tid in self.typeid:
            for offset in self.offsets:
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
        item = DongfangItem()
        item['NewsRawUrl'] = response.meta['all_link']
        item['NewsID'] = str(uuid.uuid1())
        # item['NewsCategory'] = '001.003.001'
        item['SourceCategory']= response.xpath('//*[@id="player"]/div[2]/div[1]/div[1]/div/a[1]/i/text()').extract_first()
        if item['SourceCategory'] == '资讯':
            item['NewsCategory'] = '001.003.001'
        elif item['SourceCategory'] == '娱乐':
            item['NewsCategory'] = '001.003.005'
        elif item['SourceCategory'] == '科技':
            item['NewsCategory'] = '001.003.006'
        elif item['SourceCategory'] == '财经':
            item['NewsCategory'] = '001.003.007'
        elif item['SourceCategory'] == '汽车':
            item['NewsCategory'] = '001.003.008'
        elif item['SourceCategory'] == '体育':
            item['NewsCategory'] = '001.003.010'
        elif item['SourceCategory'] == '时尚':
            item['NewsCategory'] = '001.003.012'
        elif item['SourceCategory'] == '游戏':
            item['NewsCategory'] = '001.003.016'
        elif item['SourceCategory'] == '旅游':
            item['NewsCategory'] = '001.003.017'
        elif item['SourceCategory'] == '亲子':
            item['NewsCategory'] = '001.003.018'

        item['NewsType'] = 2
        title = response.meta['title']
        item['NewsTitle'] = title
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['SourceName'] = '东方头条视频'
        NewsDate = response.meta['NewsDate']
        NewsDate_aft = datetime.datetime.strptime(NewsDate, '%Y-%m-%d %H:%M')

        item['NewsDate'] = NewsDate_aft
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        item['NewsContent'] = None

        pattern = re.compile('var mp4 = "(.*?)"', re.S)
        data = re.search(pattern, response.text).group(1)
        all_link = 'http://mv.eastday.com/' + data[19:]

        # 1.存储视频到本地
        a = File_mod(all_link)
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

        image_url = response.meta['image_url_b']
        item['image_url'] = image_url
        # 1\下载图片
        a = File_mod(image_url)
        full_name_iamge = a.Download_image()
        item['FileDirectory'] = a.detail_fdfs_file(full_name_iamge)
        a.Delete_image(full_name_iamge)

        yield item
