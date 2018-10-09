# -*- coding: utf-8 -*-
import time
import requests
import os
import uuid

from hashlib import md5
from fdfs_client.client import *
from decimal import *
from PIL import Image
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from taihainetproject.items import TaihainetprojectItem

class JunshiSpider(CrawlSpider):
    name = 'JunShi'
    # allowed_domains = ['www.taihainet.com']
    start_urls = ['http://js.taihainet.com/']

    rules = (
        Rule(LinkExtractor(allow=r'http://www.taihainet.com/news/military/^[a-z]{4}$/')),
        Rule(LinkExtractor(allow=r'/\d+\-\d+\-\d+\/\d+\.htm'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        client = Fdfs_client('/etc/fdfs/client.conf')
        item = TaihainetprojectItem()
        item['NewsID'] = '201805-' + str(uuid.uuid1())
        item['NewsCategory'] = '001.011'
        SourceCategory = response.xpath('//div[@class="list-path wrapper ovv"]/a[last()]/text() |'
                                        '//div[@class="crumb"]/a[last()]/text()').extract_first()
        # print(SourceCategory)
        # print('==================================')
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
            '//div[@class="page-info wrapper ovv"]/span[@class="important-link"]/span/text()').extract_first()
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
        if '责任编辑' in AuthorName:
            item['AuthorName'] = AuthorName[5:8]
        else:
            item['AuthorName'] = AuthorName

        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0

        # 获取图片链接
        image_urls = response.xpath(
            '//div[@class="article-content"]/p/img/@src |'
            '//ul/li[@class="current"]/a/img/@src |'
            '//ul[@class="gallery-thumb-items"]/li/a/img/@src').extract()
        try:
            content = ''.join(response.xpath(
                '//div[@class="article-content"]/p | '
                '//ul[@class="gallery-thumb-items"]/li/a/img/@alt').extract())
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
                b = round(float(a), 2)

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
            item['NewsContent'] = ''.join(response.xpath(
                '//div[@class="article-content"]/p | '
                '//div[@class="gallery-photo-description"]/p |'
                '//ul[@class="gallery-thumb-items"]/li/a/img/@alt').extract())
        item['NewsContent'] = content
        item['FileList'] = listFiles

        yield item
