# -*- coding: utf-8 -*-
import scrapy
import uuid
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from takungpaoproject.items import TakungpaoprojectItem


class TakungpaoSpider(CrawlSpider):
    name = 'takungpao'
    # allowed_domains = ['www.takungpao.com']
    start_urls = [
        'http://news.takungpao.com/world/exclusive/',  # 国际
        # 'http://ent.takungpao.com/topnews/',  # 娱乐
    ]

    # 国际
    rules = (
        Rule(LinkExtractor(allow=r'http://news.takungpao.com/world/exclusive/index_\d+\.html'), callback='parse_item', follow=True),
    )

    # 娱乐
    # rules = (
    #     Rule(LinkExtractor(allow=r'http://ent.takungpao.com/topnews/index_\d+\.html'), callback='parse_item', follow=True),
    # )

    def parse_item(self, response):
        div_list = response.xpath('//div[@class="txtImgList clearfix"]/div')
        for div in div_list:
            item = TakungpaoprojectItem()
            item['NewsID'] = str(uuid.uuid1())
            item['NewsTitle'] = div.xpath('./h3/a/text()').extract_first()
            item['NewsDate'] = div.xpath(
                './/div[@class="info"]/div[@class="funcBox"]/span[@class="time"]/text()').extract_first()
            links = div.xpath('./h3/a/@href').extract_first()

            yield scrapy.Request(url=str(links), callback=self.parse_info, meta={'item': item})

    def parse_info(self, response):
        item = response.meta['item']
        item['NewsRawUrl'] = response.url
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsType'] = 0
        item['NewsClickLike'] = 'None'
        item['NewsBad'] = 'None'
        item['NewsRead'] = 'None'
        item['NewsOffline'] = 0
        item['SourceCategory'] = '大公网'
        item['NewsContent'] = ''.join(response.xpath(
            '//div[@class="tpk_con clearfix"]/div[@class="tpk_text clearfix"]/p').extract())

        # 国际
        item['NewsCategory'] = '001.020'
        item['SourceName'] = response.xpath(
            '//div[@class="tpk_con clearfix"]//div[@class="fl_dib"][2]').extract_first()
        item['AuthorName'] = response.xpath(
            '//div[@class="tpk_con clearfix"]/div[@class="tkp_con_author clearfix"]/span/text()').extract_first()

        # 娱乐
        # item['NewsCategory'] = '001.005'
        # item['SourceName'] = response.xpath(
        #     '//div[@class="content"]//div[@class="fl_dib"]/a/text()').extract_first()
        # item['AuthorName'] = response.xpath(
        #     '//div[@class="tpk_con clearfix"]/div[@class="tkp_con_author clearfix"]/span/text()').extract_first()

        yield item
