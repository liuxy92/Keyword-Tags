# -*- coding: utf-8 -*-
import urllib
from urllib.parse import urljoin

import requests
import scrapy
from hashlib import md5
from fdfs_client.client import *
import os
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from YangZiWanBao.items import YangziwanbaoItem
from YangZiWanBao.start_url import Start_Url
from decimal import *

import uuid
import time, datetime
from PIL import Image
# from YangZiWanBao.save_fdfs import texttextrw
# from YangZiWanBao.items import MyImageItem

from YangZiWanBao.save_fdfs import fullpath

from YangZiWanBao.file_model import File_mod


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    # allowed_domains = ['yangtse.com']
    # start_urls = ['http://www.yangtse.com/app/politics/2018-03-29/538544.html']
    start_urls = [
        'http://www.yangtse.com/app/livelihood/2018-03-24/536394.html',
        'http://www.yangtse.com/app/politics/2018-03-29/538544.html'
    ]

    def parse(self, response):
        client = Fdfs_client('/etc/fdfs/client.conf')
        item = YangziwanbaoItem()
        NewsID = str(uuid.uuid1())
        item['NewsID'] = NewsID
        item['NewsCategory'] = '001.001'
        item['SourceCategory'] = "扬子晚报: " + response.xpath(
            '//*[@id="main"]/div[2]/div[1]/div/div/span/text() | //div[@class="zhaokao"]/div[@class="zhaokao-title"]/text()').extract_first()
        item['NewsType'] = 0
        item['NewsTitle'] = response.xpath(
            "//div[@class='news-main-banner']/div[@class='text-title']/text()").extract_first()
        item['NewsRawUrl'] = None
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        try:
            SourceName = \
            response.xpath("//div[@class='news-main-banner']/div[@class='text-time']/text()").extract_first().split(
                '\u3000')[0][3:]
            item['SourceName'] = "扬子晚报: " + SourceName
        except:
            item['SourceName'] = 'None'

        try:
            date = \
            response.xpath("//div[@class='news-main-banner']/div[@class='text-time']/text()").extract_first().split(
                '\u3000')[1]
            NewsDate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            item['NewsDate'] = NewsDate
        except:
            item['NewsDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0

        image_urls = response.xpath(
            "//div[@class='text-text']/p/img/@src | //div[@class='text-text']/p/a/img/@src").extract()
        content = ''.join(response.xpath(
            "//div[@class='news-main-banner']/div[@class='text-text']/p | //div[@class='text-text']/div/p").extract())

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"}

        listFiles = []
        if image_urls:
            for image_url in image_urls:
                a = File_mod(image_url, content)
                content = a.detail_file()
                full_name = a.Download_image()
                # a.Delete_image(full_name)
                # # 1\存储图片到本地
                # response = requests.get(image_url, headers=headers).content
                # fiel_name = md5(response).hexdigest()
                # file = '{0}/{1}.{2}'.format(os.getcwd(),  fiel_name, 'jpg')
                # if not os.path.exists(file):
                #     with open(file, "wb") as f:
                #         f.write(response)
                #         f.close()
                #
                # # item['image_url'] = image_url
                # # 2\判断图片是否已经存在,上传到fdfs服务器
                # a = str(os.path.getsize(os.getcwd() + "/" +fiel_name +'.jpg') / 1024)
                # b = Decimal(a).quantize(Decimal('0.00'))
                # # item['FileLength'] = b
                #
                # ret = client.upload_by_filename(os.getcwd() + "/" + fiel_name + '.jpg')
                # new_url = str(ret['Remote file_id'], encoding="utf8")
                # print(new_url)
                # # item['FileDirectory'] = new_url
                #
                # # 3\返回fdfs服务器的远程路径,替换content中的image_url
                # content = content.replace(image_url, new_url)
                # filemodel = File_mod
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
            item['NewsContent'] = ''.join(response.xpath(
                "//div[@class='news-main-banner']/div[@class='text-text']/p | //div[@class='text-text']/div/p").extract())

        item['NewsContent'] = content
        item['FileList'] = listFiles

        yield item
