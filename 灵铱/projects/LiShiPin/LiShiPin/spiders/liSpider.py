# -*- coding: utf-8 -*-
import datetime

import scrapy
import time
import uuid
import re
from LiShiPin.file_model import File_mod
from LiShiPin.items import LishipinItem


class LispiderSpider(scrapy.Spider):
    name = 'liSpider'
    # allowed_domains = ['pearvideo.com']
    # start_urls = ['http://pearvideo.com/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'

    }

    baseURl = 'http://www.pearvideo.com/category_loading.jsp?reqType=5&categoryId={0}&start={1}'
    # urls = [
    #     'http://www.pearvideo.com/category_loading.jsp?reqType=5&categoryId=10&start=0',
    #     'http://www.pearvideo.com/category_loading.jsp?reqType=5&categoryId=4&start=0',
    #     'http://www.pearvideo.com/category_loading.jsp?reqType=5&categoryId=8&start=0',
    #     'http://www.pearvideo.com/category_loading.jsp?reqType=5&categoryId=3&start=0',
    #     'http://www.pearvideo.com/category_loading.jsp?reqType=5&categoryId=31&start=0',
    #     'http://www.pearvideo.com/category_loading.jsp?reqType=5&categoryId=9&start=0'
    # ]
    tids = ['10', '4', '8', '3', '31', '9']
    starts = [i for i in range(0, 10)]

    def start_requests(self):
        for tid in self.tids:
            for start in self.starts:
                yield scrapy.Request(self.baseURl.format(tid, start), callback=self.parse_index)

    def parse_index(self, response):
        if not response:
            return None
        links = response.xpath('//div[@class="vervideo-bd"]/a/@href').extract()
        for link in links:
            all_link = "http://www.pearvideo.com/" + link
            # print('========================')
            # print(all_link)
            # print('========================')
            yield scrapy.Request(all_link, callback=self.parse_page)

        # self.start += 12
        # for tid in self.tids:
        #     yield scrapy.Request(self.baseURl.format(tid, self.start), callback=self.parse_index)

    def parse_page(self, response):
        item = LishipinItem()

        item['NewsRawUrl'] = response.url
        item['NewsID'] = str(uuid.uuid1())
        # item['NewsCategory'] = '001.003.001'
        try:
            item['SourceCategory'] = response.xpath('//*[@id="select"]/a/text()').extract_first()

            if item['SourceCategory'] == '新知':
                item['NewsCategory'] = '001.003.001'
            elif item['SourceCategory'] == '娱乐':
                item['NewsCategory'] = '001.003.005'
            elif item['SourceCategory'] == '科技':
                item['NewsCategory'] = '001.003.006'
            elif item['SourceCategory'] == '财富':
                item['NewsCategory'] = '001.003.007'
            elif item['SourceCategory'] == '汽车':
                item['NewsCategory'] = '001.003.008'
            elif item['SourceCategory'] == '体育':
                item['NewsCategory'] = '001.003.010'
            elif item['SourceCategory'] == '世界':
                item['NewsCategory'] = '001.003.001'

        except:
            item['SourceCategory'] = None
            item['NewsCategory'] = None

        item['NewsType'] = 2
        item['NewsTitle'] = response.xpath('//h1/text()').extract_first()
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        try:
            item['SourceName'] = response.xpath(
                '//div[@id="detailsbd"]/div[1]/div[3]/div[1]/div[1]/a/div/text()').extract_first()
        except:
            item['SourceName'] = '梨视频'
        try:
            date = response.xpath("//div[@class='brief-box']/div[@class='date']/text()").extract_first()
            NewsDate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
            item['NewsDate'] = NewsDate
        except:
            item['NewsDate'] = None
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        try:
            item['NewsContent'] = response.xpath(
                "//div[@class='details-content-describe']/div[@class='summary']/text()").extract_first()
        except:
            item['NewsContent'] = None

        pattern = re.compile(r'srcUrl="(.*?)"', re.S)
        all_link = re.search(pattern, response.text).group(1)

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

        image_url = response.xpath("//div[@id='poster']/img/@src").extract_first()
        item['image_url'] = image_url
        # 1\下载图片
        a = File_mod(image_url)
        full_name_iamge = a.Download_image()
        item['FileDirectory'] = a.detail_fdfs_file(full_name_iamge)
        a.Delete_image(full_name_iamge)

        yield item
