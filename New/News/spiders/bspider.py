# -*- coding: utf-8 -*-
import scrapy
import json

from ..file_model import File_mod
from ..items import NewsItem

from decimal import *
from scrapy.selector import Selector

import uuid
import time, datetime
import re
class BspiderSpider(scrapy.Spider):
    name = 'bspider'
    # allowed_domains = ['ynet.com']
    # start_urls = ['http://ynet.com/']

    # baseURL = 'http://m.ynet.com/data/getlistinfo/?channelId={0}&page={1}&num=10'
    baseURL = 'http://m.ynet.com/data/getlistinfo/?channelId={0}&page=1&num=10'

    # channelIds = ['1', '2', '8', '28', '12', '13', '26']
    channelIds = ['1', '2', '3', '11', '12', '13', '18', '19', '23', '24', '25', '26', '29', '30'] # 1是新闻 2是娱乐 3是体育 5是生活（没有） 8社会（没有） 11美食 12观天下 13探索 18军事 19搞笑 23历史 24科技 25星座 26时尚 27情感（没有） 28健康（没有） 29教育 30养生


    pages = [i for i in range(0, 3)]

    def start_requests(self):
        # yield scrapy.Request(self.baseURL, callback=self.parse_index)

        for cid in self.channelIds:
            for page in self.pages:
                yield scrapy.Request(self.baseURL.format(cid, page), callback=self.parse_index)

    def parse_index(self, response):
        result = json.loads(response.text)
        response_url = response.url
        for res in result['articles']:
            articles_url = res['newsUrlHttps']
            if '\/' in articles_url:
                pageurl = articles_url.replace('\/', '/')
                Newstitle = res['title']
                SourceName = res['media']
                Newstime = res['updateTime']
                SourceCategory = res['tags'][0]
                # print('======================')
                # print(SourceCategory)
                # print('======================')
                yield scrapy.Request(pageurl,
                                     meta={'SourceName': SourceName, 'Newstitle': Newstitle, 'Newstime': Newstime,'SourceCategory':SourceCategory, "response_url":response_url},
                                     callback=self.parse_articles)

            else:
                Newstitle = res['title']
                SourceName = res['media']
                Newstime = res['updateTime']
                SourceCategory = res['tags'][0]
                # print('======================')
                # print(SourceCategory)
                # print('======================')
                yield scrapy.Request(articles_url,
                                     meta={'SourceName': SourceName, 'Newstitle': Newstitle, 'Newstime': Newstime,'SourceCategory':SourceCategory,"response_url":response_url},
                                     callback=self.parse_articles)

    def parse_articles(self, response):
        item = NewsItem()

        now_time = datetime.datetime.now().strftime('%Y%m')
        item['NewsID'] = now_time + '-' + str(uuid.uuid1())
        SourceCategory = response.meta['SourceCategory']
        # print('==================')
        # print(SourceCategory)
        response_url = response.meta['response_url']
        item['SourceCategory'] = '北青网'
        if 'channelId=1' in response_url:
            item['SourceCategory'] = '北青网-' + '头条'
            item['NewsCategory'] = '001.001'
        elif 'channelId=2' in response_url:
            item['SourceCategory'] = '北青网-' + '娱乐'
            item['NewsCategory'] = '001.005'
        elif 'channelId=3' in response_url:
            item['SourceCategory'] = '北青网-' + '体育'
            item['NewsCategory'] = '001.010'
        elif 'channelId=3' in response_url:
            item['SourceCategory'] = '北青网-' + '体育'
            item['NewsCategory'] = '001.010'
        elif 'channelId=11' in response_url:
            item['SourceCategory'] = '北青网-' + '美食'
            item['NewsCategory'] = '001.035'
        elif 'channelId=12' in response_url:
            item['SourceCategory'] = '北青网-' + '国际'
            item['NewsCategory'] = '001.020'
        elif 'channelId=13' in response_url:
            item['SourceCategory'] = '北青网-' + '探索'
            item['NewsCategory'] = '001.013'
        elif 'channelId=18' in response_url:
            item['SourceCategory'] = '北青网-' + '军事'
            item['NewsCategory'] = '001.011'
        elif 'channelId=19' in response_url:
            item['SourceCategory'] = '北青网-' + '搞笑'
            item['NewsCategory'] = '001.032'
        elif 'channelId=23' in response_url:
            item['SourceCategory'] = '北青网-' + '历史'
            item['NewsCategory'] = '001.037'
        elif 'channelId=24' in response_url:
            item['SourceCategory'] = '北青网-' + '科技'
            item['NewsCategory'] = '001.006'
        elif 'channelId=25' in response_url:
            item['SourceCategory'] = '北青网-' + '星座'
            item['NewsCategory'] = '001.034'
        elif 'channelId=30' in response_url:
            item['SourceCategory'] = '北青网-' + '养生'
            item['NewsCategory'] = '001.014'
        elif 'channelId=29' in response_url:
            item['SourceCategory'] = '北青网-' + '教育'
            item['NewsCategory'] = '001.026'

        item['NewsType'] = 0

        Newstitle = response.meta['Newstitle']

        item['NewsTitle'] = Newstitle

        item['NewsRawUrl'] = response.url
        SourceName = response.meta['SourceName']

        item['SourceName'] = SourceName
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        Newstime = response.meta['Newstime']
        # NewsDate = datetime.datetime.strptime(Newstime, '%Y-%m-%d %H:%M:%S')
        item['NewsDate'] = Newstime


        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        result = re.sub(r'div', 'p', response.text)
        content = ''.join(Selector(text=result).xpath('//li[@id="page"]/p').extract())

        image_urls = response.xpath('//li[@id="page"]/div/img/@src').extract()
        # content = ''.join(response.xpath('//li[@id="page"]/p ').extract())
        listFiles = []
        if image_urls:
            for image_url in image_urls:
                response_url = response.url
                a = File_mod(image_url, content, response_url)
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
            item['NewsContent'] = ''.join(response.xpath('//li[@id="page"]/p').extract())
        item['NewsContent'] = content
        item['FileList'] = listFiles

        yield item


