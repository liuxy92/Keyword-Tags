# -*- coding: utf-8 -*-
import scrapy
import time,datetime
import uuid
import os
import requests
from ..file_model import File_mod
from ..items import NewsItem
from urllib.parse import urljoin
class GuangmingSpider(scrapy.Spider):
    name = 'GuangMing'
    # allowed_domains = ['www.gmw.cn']
    start_urls = ['http://www.gmw.cn/map.htm']

    def parse(self, response):
        links = response.xpath('//tr/td[@class="blue14b"]/a/@href').extract()
        for link in links:
            item = NewsItem()
            if 'http://world.gmw.cn/' == link:
                item['NewsCategory'] = '001.020'  # 国际
                yield scrapy.Request(url=link, callback=self.parse1, meta={'item': item})
            elif 'http://culture.gmw.cn/' == link:
                item['NewsCategory'] = '001.036'  # 文化
                yield scrapy.Request(url=link, callback=self.parse1, meta={'item': item})
            elif 'http://tech.gmw.cn/' == link:
                item['NewsCategory'] = '001.006'  # 科技
                yield scrapy.Request(url=link, callback=self.parse1, meta={'item': item})
            elif 'edu' in link:
                item['NewsCategory'] = '001.026'  # 教育
                yield scrapy.Request(url=link, callback=self.parse1, meta={'item': item})
            elif 'travel' in link:
                item['NewsCategory'] = '001.017'  # 旅游
                yield scrapy.Request(url=link, callback=self.parse1, meta={'item': item})
            elif 'yangsheng' in link:
                item['NewsCategory'] = '001.014'  # 养生
                yield scrapy.Request(url=link, callback=self.parse1, meta={'item': item})
            elif 'gongyi' in link:
                item['NewsCategory'] = '001.033'  # 公益
                yield scrapy.Request(url=link, callback=self.parse1, meta={'item': item})
            elif 'mil' in link:
                item['NewsCategory'] = '001.011'  # 军事
                yield scrapy.Request(url=link, callback=self.parse1, meta={'item': item})
            elif 'history' in link:
                item['NewsCategory'] = '001.037'  # 历史
                yield scrapy.Request(url=link, callback=self.parse1, meta={'item': item})
            elif 'sports' in link:
                item['NewsCategory'] = '001.010'  # 体育
                yield scrapy.Request(url=link, callback=self.parse1, meta={'item': item})
            else:
                pass

    def parse1(self, response):
        item = response.meta['item']
        links = response.xpath(
            '//div[@id="nav_world"]/ul/li/a/@href | //ul[@class="fc"]/li/a/@href | //div[@id="hoot"]/div/a/@href |'
            '//div[@id="nav_history"]/ul/li/a/@href | /html/body/div[5]/div/ul/li/a/@href | '
            '//ul[@class="subNav"]/li/a/@href'
        ).extract()
        for link in links:
            if 'node' in link:
                if 'http:' not in link:
                    u = response.url + link

                    yield scrapy.Request(url=u, callback=self.parse2, meta={'item': item})

    def parse2(self, response):
        item = response.meta['item']
        links = response.xpath(
            '//div[@class="channelLeftPart"]/div[2]/ul/li//a/@href | //span[@class="channel-newsTitle"]/a/@href'
        ).extract()
        if links is not '':
            for link in links:
                if 'content_' in link:
                    if 'http:' not in link:
                        url_info = response.url.split('node')[0] + link

                        yield scrapy.Request(url=url_info, callback=self.parse_info, meta={'item': item})

        # 获取下一页链接
        next = response.xpath('//div[@id="displaypagenum"]/center/a[@class="ptfont"][1]/@href').extract_first()
        if next:
            next_url = response.url.split('node_')[0] + next
            if '_2.htm' or '_3.htm' or '_4.htm' in next_url:

                yield scrapy.Request(url=next_url, callback=self.parse2, meta={'item': item})

    def parse_info(self, response):
        item = response.meta['item']
        i = datetime.datetime.now()
        b = "%s0%s" % (i.year, i.month)
        item['NewsID'] = '{0}-'.format(b) + str(uuid.uuid1())
        item['NewsType'] = 0
        #新闻标题
        NewsTitle = response.xpath(
            '//div[@class="contentWrapper"]/div/h1[@id="articleTitle"]/text() | //div[@id="articleTitle"]/text()'
        ).extract_first()
        if NewsTitle is not None:
            item['NewsTitle'] = NewsTitle.strip()
        else:
            item['NewsTitle'] = ''
        item['NewsDate'] = response.xpath('//div[@id="contentMsg"]/span[@id="pubTime"]/text()').extract_first()
        item['NewsRawUrl'] = response.url
        #咨询小类别
        SourceCategory = response.xpath('//div[@id="contentBreadcrumbs2"]/a[last()]/text()').extract_first()
        if SourceCategory is not None:
            item['SourceCategory'] = '光明' + str(SourceCategory)
        else:
            item['SourceCategory'] = '光明'
        #咨询来源
        SourceName = response.xpath('//span[@id="source"]/a/text()').extract_first()
        if SourceName is not None:
            item['SourceName'] = SourceName
        else:
            item['SourceName'] = '光明网'
        item['AuthorName'] = '张倩'
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0

        # 获取图片链接
        image_urls = response.xpath('//div[@id="contentMain"]//p//img/@src').extract()
        try:
            cont = ''.join(response.xpath(
                    '//div[@id="contentMain"]//p | //div[@id="ArticleContent"]/div/p | //div[@id="contentMain"]/p'
                ).extract())
            if 'https://img.gmw.cn/pic/content_logo.png' in cont:
                content = cont.replace('https://img.gmw.cn/pic/content_logo.png', '')
            else:
                content = cont
        except:
            content = 'None'
        listFiles = []
        if self.settings.get('OPEN') == 1:
            if image_urls:
                for image_url in image_urls:
                    # 1\存储图片到本地
                    # 拼接完整的图片链接
                    if 'http:' not in image_url:
                        image_url2 = urljoin(response.url, str(image_url))
                    else:
                        image_url2 = image_url
                    # 转换成能替换的src
                    if '?' in image_url2:
                        image_url_new = image_url2.split('?')[0]
                    else:
                        image_url_new = image_url2
                    # a = File_mod(image_url_new, content)
                    response_url = response.url
                    a = File_mod(image_url_new, content,response_url)
                    content = a.detail_file()
                    if 'v1' in image_url2:
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
        else:
            if image_urls:
                for image_url in image_urls:
                    if 'http:' not in image_url:
                        image_url2 = urljoin(response.url, str(image_url))
                    else:
                        image_url2 = image_url
                    # 转换成能替换的src
                    if '?' in image_url2:
                        image_url_new = image_url2.split('?')[0]
                    else:
                        image_url_new = image_url2
                    filemodel = {}
                    filemodel['FileID'] = str(uuid.uuid1())
                    filemodel['FileType'] = 0
                    filemodel['FileDirectory'] = image_url_new
                    filemodel['FileDirectoryCompress'] = None
                    filemodel['FileDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    filemodel['FileLength'] = None
                    filemodel['FileUserID'] = None
                    filemodel['Description'] = None
                    filemodel['NewsID'] = item['NewsID']
                    filemodel['image_url'] = image_url_new
                    listFiles.append(filemodel)
            else:
                item['NewsContent'] = ''.join(response.xpath('//li[@id="page"]/p').extract())
            item['NewsContent'] = content
            item['FileList'] = listFiles
            yield item


