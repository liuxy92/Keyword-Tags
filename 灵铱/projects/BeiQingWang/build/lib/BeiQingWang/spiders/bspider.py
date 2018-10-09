# -*- coding: utf-8 -*-
import scrapy
import json

from BeiQingWang.file_model import File_mod
from BeiQingWang.items import BeiqingwangItem

from decimal import *

import uuid
import time,datetime
class BspiderSpider(scrapy.Spider):
    name = 'bspider'
    # allowed_domains = ['ynet.com']
    # start_urls = ['http://ynet.com/']

    baseURL = 'http://m.ynet.com/data/getlistinfo/?channelId={0}&page={1}&num=10'
    channelIds = ['1', '2', '8', '28', '12', '13', '26']

    pages = [i for i in range(0, 11)]

    def start_requests(self):
        for cid in self.channelIds:
            for page in self.pages:
                yield scrapy.Request(self.baseURL.format(cid, page), callback=self.parse_index)

    def parse_index(self, response):
        result = json.loads(response.text)
        for res in result['articles']:
            SourceName = res['media']
            articles_url = res['newsUrlHttps']
            Newstitle = res['title']
            Newstime = res['updateTime']
            SourceCategory = res['tags'][0]
            # print('======================')
            # print(SourceCategory)
            # print('======================')
            yield scrapy.Request(articles_url,
                                 meta={'SourceName': SourceName, 'Newstitle': Newstitle, 'Newstime': Newstime,'SourceCategory':SourceCategory},
                                 callback=self.parse_articles)

    def parse_articles(self, response):
        item = BeiqingwangItem()


        item['NewsID'] = str(uuid.uuid1())
        SourceCategory = response.meta['SourceCategory']
        item['SourceCategory'] = SourceCategory
        if item['SourceCategory'] == '新闻':
            item['NewsCategory'] = '001.001'
        elif item['SourceCategory'] == '娱乐':
            item['NewsCategory'] = '001.005'
        elif item['SourceCategory'] == '社会':
            item['NewsCategory'] = '001.009'
        elif item['SourceCategory'] == '健康':
            item['NewsCategory'] = '001.014'
        elif item['SourceCategory'] == '观天下':
            item['NewsCategory'] = '001.020'
        elif item['SourceCategory'] == '探索':
            item['NewsCategory'] = '001.013'
        elif item['SourceCategory'] == '时尚':
            item['NewsCategory'] = '001.012'


        item['NewsType'] = 0

        Newstitle = response.meta['Newstitle']

        item['NewsTitle'] = Newstitle

        item['NewsRawUrl'] = response.url
        SourceName = response.meta['SourceName']

        item['SourceName'] = SourceName
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        Newstime = response.meta['Newstime']
        NewsDate = datetime.datetime.strptime(Newstime, '%Y-%m-%d %H:%M:%S')
        item['NewsDate'] = NewsDate


        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0

        image_urls = response.xpath('//li[@id="page"]/div/img/@src').extract()
        content = ''.join(response.xpath('//li[@id="page"]/p').extract())
        listFiles = []
        if image_urls:
            for image_url in image_urls:
                a = File_mod(image_url, content)
                content = a.detail_file()
                full_name = a.Download_image()
                filemodel = {}
                filemodel['FileID'] = str(uuid.uuid1())
                filemodel['FileType'] = 0
                filemodel['FileDirectory'] = a.detail_fdfs_file(full_name)
                filemodel['FileDirectoryCompress'] = a.detail_fdfs_file(full_name)
                filemodel['FileDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                filemodel['FileLength'] = a.detail_FileLength(full_name)
                filemodel['FileUserID'] = None
                filemodel['Description'] = None
                filemodel['NewsID'] = item['NewsID']
                filemodel['image_url'] = image_url
                listFiles.append(filemodel)
                a.Delete_image(full_name)
        else:
            item['NewsContent'] = ''.join(
                response.xpath('//li[@id="page"]/p').extract())
        item['NewsContent'] = content
        item['FileList'] = listFiles

        yield item


