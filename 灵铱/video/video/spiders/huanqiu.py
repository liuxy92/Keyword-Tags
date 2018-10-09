# -*- coding: utf-8 -*-
import datetime
import re
import uuid

import scrapy
import time

from video.file_model import File_mod
from video.items import VideoItem


class HuanqiuSpider(scrapy.Spider):
    name = 'huanqiu'
    allowed_domains = ['huanqiu.com']
    start_urls = ['http://mil.huanqiu.com/milmovie/']

    def parse(self, response):
        link_list = response.xpath("//ul/li/a/@href").extract()
        for link in link_list:
            # print(link)
            yield scrapy.Request(link, callback=self.parse_page)
        next_url = response.xpath("//div[@class='pageBox']//div[@id='pages']/a[@class='a1'][contains (., '下一页')]/@href").extract_first()
        #获取下一页链接
        if next_url is not None:
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_page(self, response):
        # response.encoding = 'utf-8'
        item = VideoItem()

        now_time = datetime.datetime.now().strftime('%Y%m')
        item['NewsID'] = now_time + '-' + str(uuid.uuid1())
        # item['NewsCategory'] = '001.003.001'
        item['SourceCategory'] = '环球网-军事'

        item['NewsCategory'] = '001.003.011'


        item['NewsType'] = 2
        item['NewsTitle'] = response.xpath("//div[@class='l_a']/h1/text()").extract_first()
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['SourceName'] = '环球网军事'
        item['NewsRawUrl'] = response.url

        try:
            date = response.xpath("//div[@class='la_tool']/span[@class='la_t_a']/text()").extract_first()
            # NewsDate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
            item['NewsDate'] = date
        except:
            item['NewsDate'] = 'None'
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        try:
            item['NewsContent'] = ''.join(response.xpath("//div[@class='la_con']/p/text()").extract())
        except:
            item['NewsContent'] = None

        all_link = response.xpath("//div[@id='vt-video']/video/@src").extract_first()

        if all_link:

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

            image_url = response.xpath("//div[@id='vt-video']/video/@poster").extract_first()
            item['image_url'] = image_url
            # 1\下载图片
            a = File_mod(image_url, response_url)
            full_name_iamge = a.Download_image()
            item['FileDirectory'] = a.detail_fdfs_file(full_name_iamge)
            a.Delete_image(full_name_iamge)

            yield item
