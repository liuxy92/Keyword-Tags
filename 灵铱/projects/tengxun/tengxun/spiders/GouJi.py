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
class TengxunsSpider(CrawlSpider):
    name = 'GuoJi'
    # allowed_domains = ['news.qq.com']
    start_urls = ['http://news.qq.com/']
    #http: // new.qq.com / omn / 20180418 / 20180418A059U0.html
    rules = (
        Rule(LinkExtractor(allow=r'(\w+).qq.com/(\w+)_index\.shtml'),callback='parse_item',follow=False),
        # Rule(LinkExtractor(allow=r'http://(\w+)\.qq.com/omn/2018(.*?).html'), callback='parse_item',follow=False),
        # Rule(LinkExtractor(allow=r'new/\.qq\.com/omn/.*'), callback='parse_item', follow=False),
    )

    def parse_item(self, response):
        item = TengxunItem()
        linkss = response.xpath('//div[@class="layout Q-g16b-b"]//div/div[@class="list first"]//div/div[@class="text"]/em/a/@href').extract()
        for linksss in linkss:
            link = 'http:' + str(linksss)
            yield scrapy.Request(link, meta={'info': item},callback=self.parse_page)
    def parse_page(self,response):
        print(response.url)
        client = Fdfs_client('/etc/fdfs/client.conf')
        item = response.meta['info']
        item['NewsRawUrl'] = response.url
        item['NewsID'] = str(uuid.uuid1())
        item['NewsCategory'] = '001.020'
        item['SourceCategory'] = '腾讯国际新闻网'
        item['NewsType'] = 0
        item['NewsTitle'] = response.xpath('//div[@class="qq_conent clearfix"]/div[@class="LEFT"]/h1/text()').extract_first()
        item['SourceName'] = '腾讯网'
        item['AuthorName'] = '张振'
        item['NewsDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        img_urls = response.xpath('//div[@class="LEFT"]/div/div[@class="content-article"]/p[@class="one-p"]/img/@src').extract()
        content = ''.join(response.xpath('//div[@class="qq_conent clearfix"]/div[@class="LEFT"]/div[@class="content clearfix"]/div[@class="content-article"]/p | //div[@class="content-article"]/div/div/img/@src').extract())
        listFiles = []
        if img_urls:
            for img_urlss in img_urls:
                img_url = 'http:' + str(img_urlss)
                try:
                    response = requests.get(img_url,timeout=60).content
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
            item['NewsContent'] = ''.join(response.xpath('//div[@class="qq_conent clearfix"]/div[@class="LEFT"]/div[@class="content clearfix"]/div[@class="content-article/"]/p').extract())

        item['NewsContent'] = content
        item['FileList'] = listFiles
        yield item

