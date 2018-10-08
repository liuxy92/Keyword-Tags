# -*- coding: utf-8 -*-
import scrapy
import uuid
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import ChinanewsprojectItem
from ..file_model import File_mod


class CcSpider(scrapy.Spider):
    name = 'cc'
    # allowed_domains = ['www.chinanews.com']
    start_urls = ['http://www.chinanews.com/auto/2018/04-26/8500701.shtml']

    def parse(self, response):
        print(response.url)
        item = ChinanewsprojectItem()
        item['NewsID'] = str(uuid.uuid1())
        item['NewsCategory'] = '001.010'
        item['NewsTitle'] = '量'
        item['SourceCategory'] = 'chinanews' + str(
            response.xpath('//div[@id="nav_div980"]/div[@id="nav"]/a[2]/text()').extract_first())
        item['NewsType'] = 0
        item['NewsRawUrl'] = response.url
        data = response.xpath('//div[@class="left-time"]/div[@class="left-t"]/a[2]/text()').extract_first()
        if data == '参与互动':
            item['SourceName'] = response.xpath(
                '//div[@class="left-time"]/div[@class="left-t"]/a[1]/text()').extract_first()
            item['NewsDate'] = response.xpath('//div[@class="left-time"]/div[@class="left-t"]/text()').extract_first()[
                               :-3].strip().replace('年', '-').replace('月', '-').replace('日', '') + ':00'
        else:
            try:
                item['SourceName'] = response.xpath(
                    '//div[@class="left-time"]/div[@class="left-t"]/text()').extract_first()[22:]
                item['NewsDate'] = response.xpath(
                    '//div[@class="left-time"]/div[@class="left-t"]/text()').extract_first()[:19].strip().replace('年',
                                                                                                                  '-').replace(
                    '月', '-').replace('日', '') + ':00'
            except Exception as e:
                print(e)
        item['AuthorName'] = response.xpath('//div[@class="left_name"]/div[@class="left_name"]/text()').extract_first()[
                             5:][:-2]
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        # 获取图片链接
        image_urls = response.url[:-13] + response.xpath(
            '//div[@class="content"]/div[@class="left_ph"]/img/@src').extract_first()
        content = ''.join(
            response.xpath(
                '//div[@class="content"]/div[@class="left_ph"]/img/@alt').extract())
        listFiles = []
        if image_urls is not None:
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
                response.xpath(
                    '//div[@class="content"]/div[@class="left_zw"]/div | //div[@class="content"]/div[@class="left_zw"]/p |//div[@class="content"]/div[@class="left_ph"]/img/@alt').extract())
        item['NewsContent'] = content
        item['FileList'] = listFiles
