# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import uuid
import time,datetime
from tengxun.items import TengxunItem
import os,re
from decimal import *
import requests
from hashlib import md5
from fdfs_client.client import *
from requests.exceptions import ConnectionError
path = '/home/action/桌面/image/full'
class QicheSpider(CrawlSpider):
    name = 'QiChe'
    allowed_domains = ['auto.qq.com']
    start_urls = ['http://auto.qq.com/']

    rules = (
        Rule(LinkExtractor(allow=r'auto.qq.com/(\w+).htm'),follow=True),
        Rule(LinkExtractor(allow=r'/a/2018[0-9]{4}/[0-9]{6}.htm'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        item = TengxunItem()
        item['NewsRawUrl'] = response.url
        item['NewsID'] = str(uuid.uuid1())
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
        img_urls = response.xpath('//div[@class="qq_main"]/div[@class="qq_article"]/div[@class="bd"]/div/p/img/@src').extract()
        content = ''.join(response.xpath('//div[@class="qq_main"]/div[@class="qq_article"]/div[@class="bd"]/div/p').extract())
        listFiles = []
        client = Fdfs_client('/etc/fdfs/client.conf')
        if len(img_urls) > 0:
            for img_url in img_urls:
                # print(img_url)
                try:
                    response = requests.get(img_url, timeout=60).content
                    file_name = md5(response).hexdigest()
                    file = '{0}/{1}.{2}'.format(os.getcwd(), file_name, 'jpg')
                    if not os.path.exists(file):
                        with open(file, "wb") as f:
                            f.write(response)
                            f.close()

                    # item['image_url'] = image_url
                    # 2\判断图片是否已经存在,上传到fdfs服务器
                    full_name = os.getcwd() + "/" + file_name + '.jpg'
                    a = str(os.path.getsize(full_name) / 1024)
                    b = round(float(a), 2)
                    # item['FileLength'] = b

                    ret = client.upload_by_filename(full_name)
                    new_url = str(ret['Remote file_id'], encoding="utf8")
                    # print(new_url)
                    # item['FileDirectory'] = new_url

                    # 3\返回fdfs服务器的远程路径,替换content中的image_url
                    content = content.replace(img_url, new_url)
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
                    filemodel['image_url'] = img_url
                    listFiles.append(filemodel)

                    # time.sleep(0.1)
                    # 4\删除本地文件
                    os.remove(full_name)
                except ConnectionError:
                    return None
                except requests.exceptions.MissingSchema:
                    return None
                except requests.exceptions.InvalidSchema:
                    return None
        else:
            item['NewsContent'] = ''.join(response.xpath('//div[@class="qq_main"]/div[@class="qq_article"]/div[@class="bd"]/div/p').extract())
        item['NewsContent'] = content
        item['FileList'] = listFiles
        yield item
