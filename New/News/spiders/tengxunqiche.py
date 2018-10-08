# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import uuid,re
import time,datetime
from News.items import NewsItem
from fdfs_client.client import *
from News.file_model import File_mod
class QicheSpider(CrawlSpider):
    name = 'tengxunqiche'
    allowed_domains = ['auto.qq.com']
    start_urls = ['http://auto.qq.com/']

    rules = (
        Rule(LinkExtractor(allow=r'auto.qq.com/(\w+).htm'),follow=True),
        Rule(LinkExtractor(allow=r'/a/2018[0-9]{4}/[0-9]{6}.htm'), callback='parse_item', follow=True),
    )
    custom_settings = {
        "COOKIES_ENABLED": True
    }
    def parse_item(self, response):
        item = NewsItem()
        item['NewsRawUrl'] = response.url
        i = datetime.datetime.now()
        b = "%s0%s" % (i.year, i.month)
        item['NewsID'] = '{0}-'.format(b) + str(uuid.uuid1())
        item['NewsCategory'] = '001.008'
        SourceCategory = response.xpath('//div[@class="qq_main"]/div[@class="qq_article"]/div/div/div[@class="a_Info"]/span[@class="a_catalog"]/a/text()').extract_first()
        if SourceCategory is not None:
            item['SourceCategory'] = '腾讯' + str(SourceCategory)
        else:
            item['SourceCategory'] = '腾讯网'
        item['NewsType'] = 0
        NewsTitles = response.xpath('//div[@class="qq_main"]/div[@class="qq_article"]/div/h1/text()').extract()
        if len(NewsTitles) == 0:
            pass
        else:
            item['NewsTitle'] = response.xpath('//div[@class="qq_main"]/div[@class="qq_article"]/div/h1/text()').extract_first()

        SourceNames = response.xpath('//div[@class="qq_main"]/div[@class="qq_article"]/div/div/div[@class="a_Info"]/span[@class="a_source"]/a/text()').extract()

        if len(SourceNames) == 0:
            item['SourceName'] = '腾讯汽车'
        else:
            item['SourceName'] = response.xpath('//div[@class="qq_main"]/div[@class="qq_article"]/div/div/div[@class="a_Info"]/span[@class="a_source"]/a/text()').extract_first()

        AuthorName = response.xpath('//div[@class="qq_main"]/div[@class="qq_articleFt"]/div/div[@class="qq_editor"]/text()').extract_first()
        if AuthorName == None :
            AuthorName = None
        else:
            AuthorName = AuthorName[5:]
        item['AuthorName'] = AuthorName
        item['NewsDate'] = response.xpath('//div[@class="qq_main"]/div[@class="qq_article"]/div/div/div[@class="a_Info"]/span[@class="a_time"]/text()').extract()
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        image_urls = response.xpath('//div[@class="qq_main"]/div[@class="qq_article"]/div[@class="bd"]/div/p/img/@src').extract()
        content = ''.join(response.xpath('//div[@class="qq_main"]/div[@class="qq_article"]/div[@class="bd"]/div/p').extract())
        print(content)
        listFiles = []
        if len(image_urls) > 0:
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
        if 'href' in content:
            res = re.compile(r'<a .*?>.*?</a>')
            contents = res.findall(content)
            for i in contents:
                content = content.replace(i,'')
                item['NewsContent'] = content
        else:
            item['NewsContent'] = content
        item['FileList'] = listFiles
        yield item