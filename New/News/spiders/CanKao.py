# -*- coding: utf-8 -*-
import scrapy
import uuid
import time,datetime

from ..file_model import File_mod
from ..items import NewsItem

class CankaoSpider(scrapy.Spider):
    name = 'CanKao'
    # allowed_domains = ['www.cankaoxiaoxi.com']
    start_urls = ['http://www.cankaoxiaoxi.com/']

    def parse(self, response):
        div_list = response.xpath('//nav[1]/div[@class="navWrap column"]/ul/li/a/@href').extract()
        if 'http://world.cankaoxiaoxi.com/' in div_list:
            item = NewsItem()
            item['NewsCategory'] = '001.020'
            yield scrapy.Request(url='http://world.cankaoxiaoxi.com/', callback=self.parse_url, meta={'item': item})

            if 'http://mil.cankaoxiaoxi.com/' in div_list:
                item = NewsItem()
                item['NewsCategory'] = '001.011'
                yield scrapy.Request(url='http://mil.cankaoxiaoxi.com/', callback=self.parse_url, meta={'item': item})

                if 'http://finance.cankaoxiaoxi.com/' in div_list:
                    item = NewsItem()
                    item['NewsCategory'] = '001.007'
                    yield scrapy.Request(url='http://finance.cankaoxiaoxi.com/', callback=self.parse_url, meta={'item': item})

                    if 'http://sports.cankaoxiaoxi.com/' in div_list:
                        item = NewsItem()
                        item['NewsCategory'] = '001.010'
                        yield scrapy.Request(url='http://sports.cankaoxiaoxi.com/', callback=self.parse_url, meta={'item': item})
        else:
            return None

    def parse_url(self, response):
        item = response.meta['item']
        links = response.xpath('//div[starts-with(@class,"elem ov")]/a/@href').extract()
        for link in links:

            yield scrapy.Request(url=str(link), callback=self.parse_info, meta={'item': item})

    def parse_info(self, response):
        item = response.meta['item']
        i = datetime.datetime.now()
        b = "%s0%s" % (i.year, i.month)
        item['NewsID'] = '{0}-'.format(b) + str(uuid.uuid1())
        item['NewsType'] = 0
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        SourceCategory = response.xpath('//div[@class="column"]/div/div[@class="crumb"]/a[3]/text()').extract_first()
        if SourceCategory is not None:
            item['SourceCategory'] = '参考消息' + SourceCategory
        else:
            item['SourceCategory'] = '参考消息'
        item['NewsTitle'] = response.xpath('//div[@class="bg-content"]/h1/text() | //div[@class="column"]/h1/text()').extract_first()
        item['NewsRawUrl'] = response.url
        # --------------------------------------------
        SourceName = response.xpath(
            '//div[@class="bg-content"]/span[@id="source_baidu"]/a/text() |'
            '//div[@class="picture-infos f-l"]/span[2]/a/text()').extract_first()
        if SourceName is not None:
            item['SourceName'] = SourceName
        else:
            item['SourceName'] = 'www.cankaoxiaoxi.com'
        # ---------------------------------------------
        item['AuthorName'] = response.xpath(
            '//div[@class="bg-content"]/span[@id="editor_baidu"]/text() |'
            '//div[@class="picture-infos f-l"]/span[last()]/text()').extract_first()[5:]
        NewsDate = response.xpath('//div[@class="bg-content"]/span[@id="pubtime_baidu"]/text()').extract_first()
        if NewsDate is None:
            item['NewsDate'] = response.xpath('//div[@class="picture-infos f-l"]/span[1]/text()').extract_first()[:-2] + ':00'
        else:
            item['NewsDate'] = NewsDate
        item['InsertDate'] = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))

        # 获取图片链接
        image_urls = response.xpath('//div[@class="inner"]//p//img/@src | //div[@class="inner"]/div/p//a/img/@src | //div[@class="thumb-box f-l"]/ul/li/a/img/@src').extract()
        content = ''.join(response.xpath('//div[@class="inner"]/div/p | //div[@class="thumb-box f-l"]/ul/li/a/img/@alt').extract())
        listFiles = []
        if image_urls is not None:
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
        item['NewsContent'] = content
        item['FileList'] = listFiles

        yield item




