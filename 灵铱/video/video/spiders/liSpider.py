# -*- coding: utf-8 -*-
import datetime

import scrapy
import time
import uuid
import re
from video.file_model import File_mod
from video.items import VideoItem


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
    tids = ['10', '4', '8', '3', '31', '9', '1', '59', '5', '2']
    # starts = [i for i in range(0, 10)]

    def start_requests(self):
        for tid in self.tids:
            for start in range(1, 5):
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
        item = VideoItem()

        item['NewsRawUrl'] = response.url
        now_time = datetime.datetime.now().strftime('%Y%m')
        item['NewsID'] = now_time + '-' + str(uuid.uuid1())
        # item['NewsCategory'] = '001.003.001'
        try:
            SourceCategory = response.xpath('//*[@id="select"]/a/text()').extract_first()
            if SourceCategory == '新知':
                item['SourceCategory'] = '梨视频-' + SourceCategory

                item['NewsCategory'] = '001.003.001'
            elif SourceCategory == '娱乐':
                item['SourceCategory'] = '梨视频-' + SourceCategory

                item['NewsCategory'] = '001.003.005'
            elif SourceCategory == '科技':
                item['SourceCategory'] = '梨视频-' + SourceCategory

                item['NewsCategory'] = '001.003.006'
            elif SourceCategory == '财富':
                item['SourceCategory'] = '梨视频-' + SourceCategory

                item['NewsCategory'] = '001.003.007'
            elif SourceCategory == '汽车':
                item['SourceCategory'] = '梨视频-' + SourceCategory

                item['NewsCategory'] = '001.003.008'
            elif SourceCategory == '体育':
                item['SourceCategory'] = '梨视频-' + SourceCategory

                item['NewsCategory'] = '001.003.010'
            elif SourceCategory == '世界':
                item['SourceCategory'] = '梨视频-' + SourceCategory

                item['NewsCategory'] = '001.003.020'
            elif SourceCategory == '社会':
                item['SourceCategory'] = '梨视频-' + SourceCategory

                item['NewsCategory'] = '001.003.003'
            elif SourceCategory == '音乐':
                item['SourceCategory'] = '梨视频-' + SourceCategory

                item['NewsCategory'] = '001.003.004'

        except:
            item['SourceCategory'] = None
            item['NewsCategory'] = None

        item['NewsType'] = 2
        item['NewsTitle'] = response.xpath('//h1/text()').extract_first()
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        try:
            item['SourceName'] = '梨视频-' + response.xpath('//div[@id="detailsbd"]/div[1]/div[3]/div[1]/div[1]/a/div/text()').extract_first()
        except:
            item['SourceName'] = '梨视频'
        try:
            date = response.xpath("//div[@class='brief-box']/div[@class='date']/text()").extract_first()
            # NewsDate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M')
            item['NewsDate'] = date
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

        image_url = response.xpath("//div[@id='poster']/img/@src").extract_first()
        item['image_url'] = image_url
        # 1\下载图片
        a = File_mod(image_url, response_url)
        full_name_iamge = a.Download_image()
        item['FileDirectory'] = a.detail_fdfs_file(full_name_iamge)
        a.Delete_image(full_name_iamge)

        yield item
