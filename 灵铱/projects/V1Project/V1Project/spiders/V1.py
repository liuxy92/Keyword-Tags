# -*- coding: utf-8 -*-
import scrapy
import json
import uuid
import time

from ..items import V1ProjectItem
from ..file_model import File_mod


class V1Spider(scrapy.Spider):
    name = "V1"
    def start_requests(self):
        start_url = 'http://www.v1.cn/index/getList4Ajax'

        list = [3, 5, 15, 17, 18, 23]
        for i in list:
            for j in range(5):
                item = V1ProjectItem()
                if i == 3:
                    item['NewsCategory'] = '001.003.001'
                    yield scrapy.FormRequest(
                        url=start_url,
                        formdata={"cid": "3", "page": "j"},
                        callback=self.parse_page,
                        meta={'item': item}
                    )
                elif i == 5:
                    item['NewsCategory'] = '001.003.009'
                    yield scrapy.FormRequest(
                        url=start_url,
                        formdata={"cid": "5", "page": "j"},
                        callback=self.parse_page,
                        meta={'item': item}
                    )
                elif i == 15:
                    item['NewsCategory'] = '001.003.017'
                    yield scrapy.FormRequest(
                        url=start_url,
                        formdata={"cid": "15", "page": "j"},
                        callback=self.parse_page,
                        meta={'item': item}
                    )
                elif i == 17:
                    item['NewsCategory'] = '001.003.005'
                    yield scrapy.FormRequest(
                        url=start_url,
                        formdata={"cid": "17", "page": "j"},
                        callback=self.parse_page,
                        meta={'item': item}
                    )
                elif i == 18:
                    item['NewsCategory'] = '001.003.008'
                    yield scrapy.FormRequest(
                        url=start_url,
                        formdata={"cid": "18", "page": "j"},
                        callback=self.parse_page,
                        meta={'item': item}
                    )
                elif i == 23:
                    item['NewsCategory'] = '001.003.007'
                    yield scrapy.FormRequest(
                        url=start_url,
                        formdata={"cid": "23", "page": "j"},
                        callback=self.parse_page,
                        meta={'item': item}
                    )
                else:
                    return None

            # FormRequest 是Scrapy发送POST请求的方法
            # yield scrapy.FormRequest(
            #     url=start_url,
            #     formdata={"cid": "i", "page": "1"},
            #     callback=self.parse_page,
            #     meta={'item': item}
            # )

    def parse_page(self, response):
        obj = response.text
        video_lists = json.loads(obj)
        print(video_lists)

        lists = video_lists['list']
        for list in lists:
            item = response.meta['item']
            item['NewsID'] = str(uuid.uuid1())
            item['SourceCategory'] = '第一视频'
            item['NewsType'] = 2

            # 获取视频的链接
            NewsRawUrl = 'http://www.v1.cn/video/' + str(list['vid']) + '.shtml'
            item['NewsRawUrl'] = NewsRawUrl
            item['NewsTitle'] = list['title']
            item['NewsContent'] = list['tag']
            item['SourceName'] = 'V1.cn'
            item['AuthorName'] = list['nickname']
            item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item['NewsDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item['NewsClickLike'] = 0
            item['NewsBad'] = 0
            item['NewsRead'] = 0
            item['NewsOffline'] = 0

            # 获取视频的MP4下载链接
            video_link = list['url']
            # 1.存储视频到本地
            a = File_mod(video_link)
            full_name_video = a.Download_video()


            item['FileID'] = str(uuid.uuid1())
            item['FileType'] = 0

            item['FileDirectoryCompress'] = a.detail_fdfs_file(full_name_video)
            item['FileDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item['FileLength'] = a.detail_FileLength(full_name_video)
            item['FileUserID'] = None
            item['Description'] = None
            item['NewsID'] = item['NewsID']

            image_url = list['pic']
            item['image_url'] = image_url
            # 1\下载图片
            a = File_mod(image_url)
            full_name_iamge = a.Download_image()

            item['FileDirectory'] = a.detail_fdfs_file(full_name_iamge)


            a.Delete_video(full_name_video)

            a.Delete_image(full_name_iamge)

            yield item



