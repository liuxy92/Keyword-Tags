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
from huanqiuproject.items import HuanqiuprojectItem

class HqSpider(CrawlSpider):
    name = 'QiChe'
    # allowed_domains = ['www.huanqiu.com']
    start_urls = [
        'http://auto.huanqiu.com/globalnews/?',
        'http://auto.huanqiu.com/newmodel/?',
        'http://auto.huanqiu.com/testdrive/?',
        'http://auto.huanqiu.com/purchasecar/?',
        'http://auto.huanqiu.com/maintenanceofvehicles/?',
        'http://auto.huanqiu.com/industryreview/?',
        'http://auto.huanqiu.com/toptalk/?'
    ]

    rules = (
        Rule(LinkExtractor(allow=r'http://auto.huanqiu.com/[a-z]+/\w+\.html'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        # print(response.url)
        # print('==================')
        div_list = response.xpath('//ul/li[starts-with(@class,"item")]')
        for div in div_list:
            item = HuanqiuprojectItem()
            item['NewsID'] = str(uuid.uuid1())
            item['NewsTitle'] = div.xpath('./h3/a/text()').extract_first()
            item['NewsDate'] = div.xpath('./h6/text()').extract_first()
            links = div.xpath('./h3/a/@href').extract_first()

            yield scrapy.Request(url=str(links), callback=self.parse_info, meta={'item': item})

    def parse_info(self, response):
        print(response.url)
        print('==================')
        client = Fdfs_client('/etc/fdfs/client.conf')
        item = response.meta['item']
        item['NewsCategory'] = '001.008'
        item['NewsRawUrl'] = response.url

        SourceName = response.xpath(
            '//div[@class="conText"]//a/text() | '
            '//div[@class="la_tool"]/span/a/text() | '
            '//li[@class="from"]/div[@class="item"]/span/text() |'
            '//div[@class="location lineDetail"]/a[last()]/text() |'
            '//div[@class="summary"]/strong/a/text()'
        ).extract_first()
        if SourceName is not None:
            item['SourceName'] = SourceName
        else:
            item['SourceName'] = '环球网'

        # item['AuthorName'] = response.xpath(
        #     '//div[@id="text"]/div[last()]/span/text() | '
        #     '//div[@class="la_edit"]/span/text() | '
        #     '//li[@class="user"]/div[@class="item"]/span/text() |'
        #     '//div[@class="editorSign"]/span[@id="editor_baidu"]/text()'
        # ).extract_first()[3:6]
        item['AuthorName'] = '沈达炜'

        SourceCategory = response.xpath(
            '//div[@class="nav_left"]/a[last()]/text() |'
            '//div[@class="topPath"]/a[last()]/text()'
        ).extract_first()
        if SourceCategory is not None:
            item['SourceCategory'] = '环球' + str(SourceCategory)
        else:
            item['SourceCategory'] = '环球汽车滚动新闻'
        item['NewsType'] = 0
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        # 获取图片链接
        image_urls = response.xpath(
            '//div[@class="la_con"]/p/img/@src | '
            '//div[@id="text"]/p/img[last()]/@src | '
            '//div[@id="text"]/div/p/img/@src |'
            '//div[@class="m_l"]//a/img/@src | '
            '//div[@class="la_con"]/p/img/@src'
        ).extract()
        # content = ''.join(response.xpath('//div[@class="la_con"]/p | //div[@id="text"]/p | //div[@class="la_con"]').extract())
        try:
            content = ''.join(
                response.xpath(
                    '//div[@class="la_con"]/p | '
                    '//div[@id="text"]/p | '
                    '//div[@id="text"]/div/p |'
                    '//div[@class="la_con"]/p | '
                    '//div[@class="m_l"]//a/img'
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
            item['NewsContent'] = content = ''.join(
                response.xpath(
                    '//div[@class="la_con"]/p | //div[@id="text"]/p | //div[@class="la_con"]/p | //div[@class="m_l"]//a/img').extract())
        item['NewsContent'] = content
        item['FileList'] = listFiles

        yield item