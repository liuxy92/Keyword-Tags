# -*- coding: utf-8 -*-
import scrapy
from HuaShang.items import HuashangItem

from HuaShang.file_model import File_mod
import uuid
import time, datetime

class SpiderSpider(scrapy.Spider):
    name = 'spider'
    allowed_domains = ['hsw.cn']
    start_urls = [
        'http://hsb.hsw.cn/gj',
        'http://hsb.hsw.cn/news/',
        'http://hsb.hsw.cn/sport/',
        'http://hsb.hsw.cn/fun/',
        'http://hsb.hsw.cn/finance/',
    ]

    def parse(self, response):
        links = response.xpath("//div[@class='langmubt2']/ul/li/a/@href").extract()
        SourceCategory = response.xpath("//div[@class='nanmoco']/h3/a/text()").extract_first()
        for link in links:
            # print(link)

            yield scrapy.Request(link, meta={'info': SourceCategory}, callback=self.parse_page)
        # 下一页
        next_url = response.xpath("/html/body/div[2]/div[1]/div[2]/div[2]/a[11]/@href").extract_first()
        if next_url is not None:
            yield scrapy.Request(next_url, callback=self.parse)

    def parse_page(self, response):
        item = HuashangItem()
        item['NewsID'] = str(uuid.uuid1())
        try:
            item['SourceCategory'] = response.meta['info']
            if item['SourceCategory'] == '要闻':
                item['NewsCategory'] = '001.001'
            elif item['SourceCategory'] == '国际':
                item['NewsCategory'] = '001.020'
            elif item['SourceCategory'] == '体育':
                item['NewsCategory'] = '001.010'
            elif item['SourceCategory'] == '娱乐':
                item['NewsCategory'] = '001.005'
            elif item['SourceCategory'] == '经济':
                item['NewsCategory'] = '001.007'
        except:
            item['SourceCategory'] = None
            item['NewsCategory'] = None

        item['NewsType'] = 0
        try:
            item['NewsTitle'] = response.xpath("//div[@class='article']/div[@class='hd']/h1/text()").extract_first()
        except:
            item['NewsTitle'] = None

        item['NewsRawUrl'] = response.url
        item['SourceName'] = '华商报'
        # try:
        #     item['SourceName'] = response.xpath("//div[@class='tit-bar']/div/span[1]/a/@href").extract_first()
        # except:
        #     item['SourceName'] = None
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # item['NewsDate'] = response.xpath("//div[@class='left-wrapper']/div[@class='meta']/span/text()").extract_first()
        try:
            # item['NewsDate'] = datetime.datetime.strptime(response.meta['date'],'%Y-%m-%d %H:%M:%S')
            date = response.xpath("//div[@class='tit-bar']/div/span[2]//text()").extract_first()
            NewsDate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            item['NewsDate'] = NewsDate
        except:
            item['NewsDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0

        image_urls = response.xpath("//div[@class='es-carousel']/ul/li/img/@src").extract()
        content = ''.join(response.xpath("//div[@class='article']/div[@class='contentBox']/p").extract())
        listFiles = []
        if image_urls:
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
                response.xpath("//div[@class='article']/div[@class='contentBox']/p").extract())
        item['NewsContent'] = content
        item['FileList'] = listFiles

        yield item

