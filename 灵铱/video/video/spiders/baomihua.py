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
from urllib.parse import urljoin

class HuanqiuSpider(scrapy.Spider):
    name = 'baomihua'
    # allowed_domains = ['huanqiu.com']
    # start_urls = ['http://mil.huanqiu.com/milmovie/']
    baseURL = 'http://www.baomihua.com/interfaces/getindexinfo.ashx?datatype=VideoListRec&typeid={0}&pagesize=20&curpage={1}&scenetype=pc_channel'
    # typeid = 101 curpage = 1 娱乐
    # typeid: 1  curpage: 1  美食
    # typeid: 108 科技
    # typeid: 13 汽车
    typeids = [3, 101, 1, 108, 13]
    def start_requests(self):
        for typeid in self.typeids:
            for page in range(1,6):
                yield scrapy.Request(self.baseURL.format(typeid, page), callback=self.parse_index)


    def parse_index(self, response):
        results = json.loads(response.text)
        response_url = response.url
        if not results:
            return
        for vlist in results.get('Videolist'):

            appName_u = vlist.get('appName')
            appName = urllib.parse.unquote(appName_u)

            videoTitle_u = vlist.get('videoTitle')
            videoTitle = urllib.parse.unquote(videoTitle_u)

            videoImgUrl = vlist.get('videoImgUrl')
            videoPlayUrl = vlist.get('videoPlayUrl')
            allPlayUrl = urljoin(response.url, videoPlayUrl)
            yield scrapy.Request(allPlayUrl, meta={"videoTitle": videoTitle, "videoImgUrl": videoImgUrl,'videoPlayUrl': videoPlayUrl, 'response_url': response_url}, callback=self.get_video)


    def get_video(self, response):
        item = VideoItem()
        now_time = datetime.datetime.now().strftime('%Y%m')
        item['NewsID'] = now_time + '-' + str(uuid.uuid1())
        # item['NewsCategory'] = '001.003.001'
        response_url = response.meta['response_url']
        if 'typeid=3' in response_url:
            item['SourceCategory'] = '爆米花视频-搞笑'  # 改为 爆米花+分类
            item['NewsCategory'] = '001.003.021'
        elif 'typeid=101' in response_url:
            item['SourceCategory'] = '爆米花视频-娱乐'
            item['NewsCategory'] = '001.003.005'
        elif 'typeid=1' in response_url:
            item['SourceCategory'] = '爆米花视频-美食'
            item['NewsCategory'] = '001.003.014'
        elif 'typeid=108' in response_url:
            item['SourceCategory'] = '爆米花视频-科技'
            item['NewsCategory'] = '001.003.006'
        elif 'typeid=13' in response_url:
            item['SourceCategory'] = '爆米花视频-汽车'
            item['NewsCategory'] = '001.003.008'



        item['NewsType'] = 2
        item['NewsTitle'] = response.meta['videoTitle']
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['SourceName'] = '爆米花视频'  # 改为视频的来源
        item['NewsDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        videoPlayUrl = response.meta['videoPlayUrl']
        allPlayUrl = urljoin(response.url, videoPlayUrl)
        item['NewsRawUrl'] = allPlayUrl

        item['NewsContent'] = None

        # 通过you-get 方法获取到视频的真实地址，--url/-u,--json
        # allurl = subprocess.getstatusoutput('you-get -u {0}'.format(item['NewsRawUrl']))
        allurl = subprocess.getstatusoutput('you-get --json {0}'.format(allPlayUrl))
        print('=====================')
        print(allurl)

        if allurl is not None:
            # results = re.findall(r'URLs:(.*)', str(allurl))
            results = json.loads(allurl[1])
            result = results['streams']['__default__']['src'][0]
            # print(results)
            # result = results[0][2:-2]
            response_url = response.url

            # 1.存储视频到本地
            a = File_mod(result, response_url)
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
            # all_image_url = urljoin(response.url, image_url)
            item['image_url'] = image_url
            # 1\下载图片
            a = File_mod(item['image_url'], response_url)
            full_name_iamge = a.Download_image()
            item['FileDirectory'] = a.detail_fdfs_file(full_name_iamge)
            a.Delete_image(full_name_iamge)

            yield item
