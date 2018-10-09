# -*- coding: utf-8 -*-
import scrapy


class TextSpider(scrapy.Spider):
    name = 'text'
    # allowed_domains = ['www.huanqiu.com']
    start_urls = ['http://tech.huanqiu.com/discovery/2016-10/9513001.html',
                  'http://tech.huanqiu.com/discovery/2016-11/9615697.html',
                  'http://tech.huanqiu.com/discovery/2016-10/9513035.html',
                  'http://tech.huanqiu.com/discovery/2016-11/9702459.html',
                  'http://world.huanqiu.com/article/2018-04/11833689.html'
                  ]

    def parse(self, response):
        Name = response.xpath(
            '//div[@class="conText"]//a/text() | '
            '//div[@class="la_tool"]/span/a/text() | '
            '//li[@class="from"]/div[@class="item"]/span/text() |'
            '//div[@class="summaryNew"]/strong[@class="fromSummary"]/a/text()'
        ).extract_first()

        if Name is not None:
            if Name == ' ':
                SourceName = Name.replace(' ', '环球网')
            else:
                SourceName = Name
        else:
            SourceName = '环球网'

        # if Name is None:
        #     SourceName = '环球网'
        # else:
        #     SourceName = Name
        print(SourceName)
        print('=============================')
