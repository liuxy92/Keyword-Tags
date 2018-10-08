# -*- coding: utf-8 -*-
import scrapy
import time,datetime
import requests
import uuid
import os

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..file_model import File_mod
from ..items import NewsItem


class TaihaiSpider(CrawlSpider):
    name = 'TaiHai'
    # allowed_domains = ['www.taihainet.com']
    start_urls = ['http://www.taihainet.com/']

    rules = (
        Rule(LinkExtractor(allow=r'http://[a-z]{2}\.taihainet.com/$'), follow=True),
        Rule(LinkExtractor(allow=r'http://www.taihainet.com/news/[a-z]{7,8}/[a-z]{2,8}/$'), follow=True),
        Rule(LinkExtractor(allow=r'http://www.taihainet.com/news/[a-z]{7,8}/[a-z]{2,8}/2018-[0-9]{2}-[0-9]{2}/(\d+).html'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = NewsItem()
        i = datetime.datetime.now()
        b = "%s0%s" % (i.year, i.month)
        item['NewsID'] = '{0}-'.format(b) + str(uuid.uuid1())
        link = response.url
        if 'finance' in link:
            item['NewsCategory'] = '001.007'  # 财经
        elif 'military' in link:
            item['NewsCategory'] = '001.011'  # 军事
        elif 'pastime' in link:
            item['NewsCategory'] = '001.005'  # 娱乐
        elif 'xmwgy' in link:
            item['NewsCategory'] = '001.033'  # 公益
        else:
            item['NewsCategory'] = ''
        # 资源小分类
        SourceCategory = response.xpath('//div[@class="list-path wrapper ovv"]/a[last()]/text() |'
                                        '//div[@class="crumb"]/a[last()]/text()').extract_first()
        if SourceCategory is None:
            item['SourceCategory'] = '台海'
        else:
            item['SourceCategory'] = '台海' + str(SourceCategory)
        item['NewsType'] = 0
        item['NewsTitle'] = response.xpath(
            '//hgroup[@class="wrapper"]/h1/text() |'
            '//div[@class="picture-main"]/header/h1/text()').extract_first()
        item['NewsDate'] = response.xpath(
            '//div[@class="page-info"]/span[2]/text() |'
            '//div[@class="page-info wrapper ovv"]/time/text() |'
            '//div[@class="picture-infos"]/span[@class="post-time"]/text() |'
            '//span[@id="pubtime_baidu"]/text() |'
            '//span[@class="post-time"]/text()'
        ).extract_first().rstrip() + ':00'
        item['NewsRawUrl'] = response.url
        # 文章来源
        SourceName = response.xpath(
            '//span[@class="source_baidu"]/a/text() | '
            '//div[@class="picture-infos"]/span[@class="source"]/a/text() |'
            '//div[@class="page-info wrapper ovv"]/span[@class="important-link"]/span/text()'
        ).extract_first()
        if SourceName is not None:
            if ' ' in SourceName:
                item['SourceName'] = SourceName.strip()
            else:
                item['SourceName'] = SourceName
        else:
            item['SourceName'] = '台海网'
        # 文章作者
        AuthorName = response.xpath(
            '//div[@class="article-footer"]//span/text() |'
            '//div[@class="picture-infos"]/span[@class="editor"]/text() |'
            '//ul[@class="contentfooter"]/li[2]/span/text()').extract_first()
        if AuthorName is not None:
            if '责任编辑' in AuthorName:
                item['AuthorName'] = AuthorName[5:8]
            else:
                item['AuthorName'] = AuthorName
        else:
            item['AuthorName'] = ''
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0

        # 获取图片链接
        image_urls = response.xpath(
            '//div[@class="article-content"]/p//img/@src |'
            '//ul/li[@class="current"]/a/img/@src |'
            '//ul[@class="gallery-thumb-items"]/li/a/img/@src |'
            '//div[@class="article-content"]/p/video/@src').extract()
        try:
            content = ''.join(response.xpath(
                '//div[@class="article-content"]/p | '
                '//div[@class="gallery-photo-description"]/p |'
                '//ul[@class="gallery-thumb-items"]/li/a/img/@alt').extract())
        except:
            content = 'None'
        listFiles = []
        if image_urls is not None:
            for image_url in image_urls:
                if '?' in image_url:
                    image_url_new = image_url.split('?')[0]
                else:
                    image_url_new = image_url
                response_url = response.url
                a = File_mod(image_url_new, content, response_url)
                content = a.detail_file()
                if 'v1' in image_url:
                    full_name = a.Download_video()
                else:
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
