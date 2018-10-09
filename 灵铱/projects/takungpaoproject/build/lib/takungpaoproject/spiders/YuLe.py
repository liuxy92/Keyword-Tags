# -*- coding: utf-8 -*-
import scrapy
import uuid
import time
import requests
import os

from hashlib import md5
from fdfs_client.client import *
from decimal import *
from PIL import Image
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from takungpaoproject.items import TakungpaoprojectItem

class YuleSpider(CrawlSpider):
    name = 'YuLe'
    # allowed_domains = ['www.takungpao.com']
    start_urls = [
        'http://ent.takungpao.com/star/',
        'http://ent.takungpao.com/movie/',
        'http://ent.takungpao.com/tv/',
    ]

    rules = (
        Rule(LinkExtractor(allow=r'http://ent.takungpao.com/[a-z]+/index.*\.htm'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        # print(response.url)
        # print('=====================')
        div_list = response.xpath('//div[@class="introBox"]/h3/a')
        for div in div_list:
            item = TakungpaoprojectItem()
            item['NewsTitle'] = div.xpath('./text()').extract_first()
            link = div.xpath('./@href').extract_first()

            yield scrapy.Request(url=str(link), callback=self.parse_info, meta={'item': item})


    def parse_info(self, response):
        print(response.url)
        print('======================')
        client = Fdfs_client('/etc/fdfs/client.conf')
        item = response.meta['item']
        item['NewsID'] = str(uuid.uuid1())
        item['NewsCategory'] =  '001.005'
        item['SourceCategory'] = '大公网娱乐新闻'
        item['NewsType'] = 0
        item['NewsRawUrl'] = response.url

        SourceName = response.xpath(
            '//div[@class="fl_dib"][2]/a/text() |'
            '//div[@class="fl_dib"][1]/a/text()'
            ).extract_first()
        if SourceName is None:
            item['SourceName'] = str(response.xpath('//div[@class="fl_dib"][2]/text()').extract_first())[3:]
        else:
            item['SourceName'] = SourceName
        # 作者
        try:
            item['AuthorName'] = str(response.xpath('//div[@class="tkp_con_author clearfix"]/span/text()').extract_first())[5:]
        except:
            item['AuthorName'] = 'None'

        item['InsertDate'] = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))

        NewsDate = response.xpath('//div[@class="fl_dib"][1]/text()').extract_first()
        if '来源:' in NewsDate:
            item['NewsDate'] = NewsDate[:-6]
        else:
            item['NewsDate'] = NewsDate
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0

        # 获取图片链接
        image_urls = response.xpath(
            '//div[@class="tpk_con clearfix"]/div[@class="tpk_text clearfix"]/p/img/@src |'
            '//ul[@id="content"]/li/a/img/@src |'
            '//div[@id="scrollPicMain"]/ul/li/a/img/@src'
        ).extract()
        try:
            content = ''.join(
                response.xpath(
                    '//div[@class="tpk_con clearfix"]/div[@class="tpk_text clearfix"]/p |'
                    '//div[@id="conTxtZyao"]/div |'
                    '//div[@id="conTxtZyao"]/div[@class="info_txt fr_dib"]'
                ).extract())
        except:
            content = 'None'
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36 "}
        listFiles = []
        if image_urls:
            for image_url in image_urls:

                # 1\存储图片到本地
                response = requests.get(image_url, headers=headers, timeout=60).content
                file_name = md5(response).hexdigest()
                file = '{0}/{1}.{2}'.format(os.getcwd(), file_name, 'jpg')
                if not os.path.exists(file):
                    with open(file, "wb") as f:
                        f.write(response)
                        f.close()

                # 2\判断图片是否已经存在,上传到fdfs服务器
                full_name = os.getcwd() + "/" + file_name + '.jpg'
                a = str(os.path.getsize(full_name) / 1024)
                b = Decimal(a).quantize(Decimal('0.00'))

                ret = client.upload_by_filename(full_name)
                new_url = str(ret['Remote file_id'], encoding="utf8")

                # 3\返回fdfs服务器的远程路径,替换content中的image_url
                content = content.replace(image_url, new_url)
                filemodel = {}
                filemodel['FileID'] = str(uuid.uuid1())
                filemodel['FileType'] = 0
                filemodel['FileDirectory'] = new_url
                filemodel['FileDirectoryCompress'] = new_url
                filemodel['FileDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                filemodel['FileLength'] = b
                filemodel['FileUserID'] = None
                filemodel['Description'] = None
                filemodel['NewsID'] = item['NewsID']
                filemodel['image_url'] = image_url
                listFiles.append(filemodel)

                # time.sleep(0.1)
                # 4\删除本地文件
                os.remove(full_name)

        else:
            item['NewsContent'] = ''.join(
                response.xpath(
                    '//div[@class="tpk_con clearfix"]/div[@class="tpk_text clearfix"]/p |'
                    '//div[@id="conTxtZyao"]/div[@class="info_txt fr_dib"]').extract())
        item['NewsContent'] = content
        item['FileList'] = listFiles

        yield item

