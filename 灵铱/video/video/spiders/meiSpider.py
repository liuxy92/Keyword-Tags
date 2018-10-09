# -*- coding: utf-8 -*-
import json
import uuid
from fdfs_client.client import *
import scrapy
import time, datetime
from pyquery import PyQuery as pq
import requests

from video.file_model import File_mod
from video.items import VideoItem
# from jie_mi_bs import decode
import os
from hashlib import md5

from video.jie_mi_bs import decode

class MeispiderSpider(scrapy.Spider):
    name = 'meiSpider'
    allowed_domains = ['meipai.com']
    start_urls = ['http://www.meipai.com/medias/hot']
    # baseURL = 'http://www.meipai.com/home/hot_timeline?page={0}&count=12'
    baseURL = 'http://www.meipai.com/topics/news_timeline?page={0}&count=50&tid={1}'
    # pages = [i for i in range(1, 10)]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    }
    # urls = ['http://www.meipai.com/topics/news_timeline?page=1&count=24&tid=5872639793429995335',
    #         'http://www.meipai.com/topics/news_timeline?page=1&count=24&tid=5879621667768487138'
    #         ]

    tids = ['5872639793429995335', '5879621667768487138', '13', '5871155236525660080', '5870490265939297486']  # tid=13搞笑，tid: 5871155236525660080音乐
    # tids = ['5872639793429995335']  # tid=13搞笑，tid: 5871155236525660080音乐
    client = Fdfs_client('/etc/fdfs/client.conf')

    listFiles = []
    # 5872639793429995335运动
    # 5879621667768487138 游戏
    # 13搞笑
    # 5871155236525660080 音乐
    # 5870490265939297486 美食
    # tids = ['5872639793429995335']

    def start_requests(self):
        for tid in self.tids:
            for page in range(1, 6):
                yield scrapy.Request(self.baseURL.format(page, tid), callback=self.parse_index)
            # yield scrapy.Request("http://www.meipai.com/home/hot_timeline?page=1&count=12", callback=self.parse_index)

    def parse_index(self, response):
        results = json.loads(response.text)
        response_url = response.url
        if not results:
            return None
        for item in results['medias']:
            id = item.get("id")
            image_url = item.get('cover_pic')
            title = item.get('caption_complete')
            video_url = item.get('url')

            if 'live' not in video_url:
                yield scrapy.Request(video_url, meta={'image_url': image_url, 'title': title, 'video_url': video_url,'response_url':response_url},
                                     callback=self.parse_video, headers=self.headers)
                # all_link = "http://www.meipai.com/media/" + str(id)
                # # print(all_link)

        # self.page += 1
        # for tid in self.tids:
        #     yield scrapy.Request(self.baseURL.format(self.page, tid), callback=self.parse_index)

    def parse_video(self, response):
        item = VideoItem()
        item['NewsRawUrl'] = response.meta['video_url']
        now_time = datetime.datetime.now().strftime('%Y%m')
        item['NewsID'] = now_time + '-' + str(uuid.uuid1())


        # SourceCategory = response.xpath('/html/body/div[3]/div[1]/a[2]/text()').extract_first().strip()
        # print('==========================')
        # print(SourceCategory)
        response_url = response.meta['response_url']

        if 'tid=5872639793429995335' in response_url:
            item['SourceCategory'] = '美拍-' + '运动'
            item['NewsCategory'] = '001.003.001'

        elif 'tid=5879621667768487138' in response_url:
            item['SourceCategory'] = '美拍-' + '游戏'
            item['NewsCategory'] = '001.003.016'

        elif 'tid=13' in response_url:
            item['SourceCategory'] = '美拍-' + '搞笑'

            item['NewsCategory'] = '001.003.021'
        elif 'tid=5871155236525660080' in response_url:
            item['SourceCategory'] = '美拍-' + '音乐'
            item['NewsCategory'] = '001.003.004'

        elif 'tid=5870490265939297486' in response_url:
            item['SourceCategory'] = '美拍-' + '美食'
            item['NewsCategory'] = '001.003.014'


        item['NewsType'] = 2
        title = response.meta['title']
        item['NewsTitle'] = title
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['SourceName'] = '美拍视频'
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
            # 1、下载视频
            downloaded_links = decode(downloaded_links_bef)
            response_video = requests.get(downloaded_links, headers=self.headers, timeout=60).content

            file_name_video = md5(response_video).hexdigest()
            file_video = '{0}/{1}.{2}'.format(os.getcwd(), file_name_video, 'jpg')
            if not os.path.exists(file_video):
                with open(file_video, "wb") as f:
                    f.write(response_video)
                    f.close()
            full_name_video = os.getcwd() + "/" + file_name_video + '.jpg'
            a = str(os.path.getsize(full_name_video) / 1024)
            b = round(float(a), 2)

            ret_video = self.client.upload_by_filename(full_name_video)
            new_url_video = str(ret_video['Remote file_id'], encoding="utf8")

            item['FileID'] = str(uuid.uuid1())
            item['FileType'] = 2

            item['FileDirectoryCompress'] = new_url_video
            item['FileDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item['FileLength'] = b
            item['FileUserID'] = None
            item['Description'] = None
            item['NewsID'] = item['NewsID']

            # 2、下载图片
            item['image_url'] = image_url
            response_image = requests.get(image_url, headers=self.headers, timeout=60).content

            file_name_image = md5(response_image).hexdigest()
            file_image = '{0}/{1}.{2}'.format(os.getcwd(), file_name_image, 'jpg')
            if not os.path.exists(file_image):
                with open(file_image, "wb") as f:
                    f.write(response_image)
                    f.close()

            full_name_image = os.getcwd() + "/" + file_name_image + '.jpg'

            ret_image = self.client.upload_by_filename(full_name_image)
            new_url_iamge = str(ret_image['Remote file_id'], encoding="utf8")

            item['FileDirectory'] = new_url_iamge

            # 4\删除本地文件
            os.remove(full_name_video)
            os.remove(full_name_image)

            yield item

        # # print(downloaded_links)
        # # 1.存储视频到本地
        #     response_url = response.url
        #     a = File_mod(downloaded_links, response_url)
        #     full_name_video = a.Download_video()
        #
        #     item['FileID'] = str(uuid.uuid1())
        #     item['FileType'] = 2
        #
        #     item['FileDirectoryCompress'] = a.detail_fdfs_file(full_name_video)
        #     item['FileDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #     item['FileLength'] = a.detail_FileLength(full_name_video)
        #     item['FileUserID'] = None
        #     item['Description'] = None
        #     item['NewsID'] = item['NewsID']
        #     a.Delete_image(full_name_video)
        #
        #     item['image_url'] = image_url
        #     # 1\下载图片
        #     a = File_mod(image_url, response_url)
        #     full_name_iamge = a.Download_image()
        #     item['FileDirectory'] = a.detail_fdfs_file(full_name_iamge)
        #     a.Delete_image(full_name_iamge)
        #
        #     yield item
