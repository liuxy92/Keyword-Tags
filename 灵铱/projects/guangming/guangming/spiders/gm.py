# -*- coding: utf-8 -*-
import scrapy
import time
import datetime
import random, string
import uuid

from guangming.items import GuangmingItem

class GmSpider(scrapy.Spider):
    name = 'gm'
    # allowed_domains = ['http://www.gmw.cn/map.htm']
    start_urls = ['http://www.gmw.cn/map.htm']

    def parse(self, response):
        div_list = response.xpath('//div[@id="map"]//tr[position()>1]')
        for div in div_list:
            item = GuangmingItem()
            newsurl = div.xpath('./td[last()]/span/a/@href').extract_first()
            item['NewsID'] = str(uuid.uuid1())
            item['NewsRawUrl'] = newsurl
            # item['NewsCategory'] = div.xpath('./td/a/text()').extract_first()
            # item['SourceCategory'] = div.xpath('./td[last()]/span/a/text()').extract_first()
            item['NewsCategory'] = ''
            item['SourceCategory'] = '中国'
            item['NewsType'] = 0
            item['NewsClickLike'] = 'None'
            item['NewsBad'] = 'None'
            item['NewsRead'] = 'None'
            item['NewsOffline'] = 0

            if newsurl:
                yield scrapy.Request(url=newsurl, callback=self.parse_title, meta={'item': item})
            else:
                print('出错了')

    def parse_title(self, response):
        item = response.meta['item']
        div_list1 = response.xpath('//div/ul[@class="channel-newsGroup"]/li')
        for div1 in div_list1:
            # item['NewsTitle'] = div1.xpath('./a/text()').extract_first()
            # item['NewsDate'] = div1.xpath('./span/text()').extract_first()
            title_url = item['NewsRawUrl'].split('.cn')[0] + '.cn/' + str(div1.xpath('./a/@href').extract_first())

            yield scrapy.Request(url=title_url, callback=self.parse_info, meta={'item': item})

    def parse_info(self, response):
        item = response.meta['item']
        item['NewsTitle'] = response.xpath('//div[@class="contentLeft"]/h1/text()').extract_first()
        item['NewsDate'] = response.xpath('//div[@id="contentMsg"]/span[@id="pubTime"]/text()').extract_first()
        item['SourceName'] = response.xpath('//div[@id="contentMsg"]/span[@id="source"]/a/text()').extract_first()
        item['AuthorName'] = response.xpath('//div[@id="contentLiability"]/text()').extract_first()
        item['NewsContent'] = response.xpath('//div[@id="contentMain"]/p/text()').extract_first()
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        yield item
