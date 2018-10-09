# -*- coding: utf-8 -*-
import scrapy


class TextSpider(scrapy.Spider):
    name = 'text'
    # allowed_domains = ['www.taihainet.com']
    start_urls = [
          'http://www.taihainet.com/news/pastime/yllq/2018-04-10/2120755.html#g2120755=1',
          'http://www.taihainet.com/news/fujian/shms/2018-03-06/2109378.html#g2109378=1'
    ]

    def parse(self, response):
        item = response.xpath(
            # '//div[@class="picture-main"]//div[@class="picture-infos"]//a/text()'
            '/html/body/section[1]/div[2]/header/div/span[2]/text()'
            ).extract_first()
        # print(item)
        if item is not None:
            if ' ' in item:
                lll = item.strip()
            else:
                lll = item
            # lll = item
        else:
            lll = '环球'
        print(lll)
        print('=======================')



