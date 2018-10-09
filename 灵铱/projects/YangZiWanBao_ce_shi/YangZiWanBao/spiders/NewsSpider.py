# -*- coding: utf-8 -*-
# import sys
# sys.path.append('/home/action/桌面/lingyiSpider/YangZiWanBao')
import re
import requests

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
import time,datetime
from PIL import Image
# from YangZiWanBao.save_fdfs import texttextrw
# from YangZiWanBao.items import MyImageItem

from YangZiWanBao.save_fdfs import fullpath

from YangZiWanBao.file_model import File_mod
# import YangZiWanBao.file_model.File_mod
# from YangZiWanBao.items import MyImageItem
from requests.exceptions import ConnectionError
path = '/home/action/桌面/image/full'

class NewsspiderSpider(CrawlSpider):
    name = 'NewsSpider'
    # allowed_domains = ['yangtse.com']
    # start_urls = Start_Url.urls
    start_urls = [
        "http://www.yangtse.com/app/livelihood/",
        "http://www.yangtse.com/app/zhengzai/",
        "http://www.yangtse.com/app/jiangsu/kanjiangsu",
        "http://www.yangtse.com/app/jiangsu/nanjing/",
        "http://www.yangtse.com/app/politics/",
        "http://www.yangtse.com/shiping/",
        "http://www.yangtse.com/app/qinggan/",
        "http://www.yangtse.com/app/finance/",
        "http://www.yangtse.com/app/health/",
        "http://www.yangtse.com/app/education/",
        "http://www.yangtse.com/app/ent/",
        "http://www.yangtse.com/app/bzxc/",
        "http://www.yangtse.com/app/sports/",
        "http://www.yangtse.com/app/fashion/",
        "http://www.yangtse.com/app/internet/",
        "http://house.yangtse.com/",
        "http://www.yangtse.com/app/zhongguo/",
        "http://www.yangtse.com/app/world/"
    ]
    rules = (
        # Rule(LinkExtractor(allow=r'http://www\.yangtse\.com/app/(.*?)'), callback='parse_item', follow=False),

        Rule(LinkExtractor(allow=r'/index_(\d+)\.html'), callback='parse_item', follow=False),
    )

    def parse_item(self, response):
        item = YangziwanbaoItem()
        links = response.xpath("//div[@class='main-left left white']/div/div/div[@class='box-text-title']/a/@href").extract()
        for link in links:
            yield scrapy.Request(link, meta={'info': item}, callback=self.parse_page)

    def parse_page(self, response):
        client = Fdfs_client('/etc/fdfs/client.conf')
        item = response.meta['info']
        item['NewsRawUrl'] = response.url

        item['NewsID'] = str(uuid.uuid1())
        item['NewsCategory'] = '001.001'
        item['SourceCategory'] = "扬子晚报" + response.xpath('//*[@id="main"]/div[2]/div[1]/div/div/span/text() | //div[@class="zhaokao"]/div[@class="zhaokao-title"]/text()').extract_first()
        item['NewsType'] = 0
        item['NewsTitle'] = response.xpath("//div[@class='news-main-banner']/div[@class='text-title']/text()").extract_first()

        image_urls = response.xpath("//div[@class='text-text']/p/img/@src | //div[@class='text-text']/p/a/img/@src | //div[@id='content']/div/img/@src | //*[@id='js_content']/p/img/@src").extract()
        item['AuthorName'] = None
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        SourceName = response.xpath("//div[@class='news-main-banner']/div[@class='text-time']/text()").extract_first().split('\u3000')[0][2:]
        item['SourceName'] = "扬子晚报-" + SourceName

        try:
            date = response.xpath("//div[@class='news-main-banner']/div[@class='text-time']/text()").extract_first().split('\u3000')[1]
            NewsDate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            item['NewsDate'] = NewsDate
        except:
            item['NewsDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0

        content = ''.join(response.xpath("//div[@class='news-main-banner']/div[@class='text-text']/p | //div[@id='content']/div[position()>1]/text() | //div[@id='content']/div/text() | //*[@id='js_content']/section/section/p | //*[@id='js_content']/section/section/section/p | //*[@id='js_content']/p | //*[@id='content']/div/div/text()" ).extract())
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36 " }
        listFiles = []
        if image_urls:
            for image_url in image_urls:

                # 1\存储图片到本地
                try:
                    response = requests.get(image_url, headers=headers, timeout=60).content


                    file_name = md5(response).hexdigest()
                    file = '{0}/{1}.{2}'.format(os.getcwd(),  file_name, 'jpg')
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
                except ConnectionError:
                    return None
                except requests.exceptions.MissingSchema:
                    return None
                except requests.exceptions.InvalidSchema:
                    return None


        else:
            item['NewsContent'] = ''.join(response.xpath("//div[@class='news-main-banner']/div[@class='text-text']/p | //div[@id='content']/div[position()>1]/text() | //div[@id='content']/div/text() | //*[@id='js_content']/section/section/p | //*[@id='js_content']/section/section/section/p | //*[@id='js_content']/p | //*[@id='content']/div/div/text()").extract())

        item['NewsContent'] = content
        item['FileList'] = listFiles


        yield item





















