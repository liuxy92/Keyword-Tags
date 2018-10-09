# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from fenghuang.items import FenghuangItem
import uuid
import requests
from hashlib import md5
import re
import datetime
from fdfs_client.client import *
from requests.exceptions import ConnectionError
from decimal import *
class FenghuangsSpider(CrawlSpider):
    name = 'fenghuangs'
    allowed_domains = ['ifeng.com']
    start_urls = ['http://news.ifeng.com/']

    rules = (
        Rule(LinkExtractor(allow=r'(\w+).ifeng.com/$'), follow=True),
        Rule(LinkExtractor(allow=r'(\w+).ifeng.com/a/2018[0-9]{4}/(\d+)_\d\.shtml'), callback='parse_item', follow=False),
    )

    def parse_item(self, response):
        # print(response.url)
        item = FenghuangItem()
        item['NewsRawUrl'] = response.url
        item["NewsID"] = '201805-' + str(uuid.uuid1())
        NewsCategorys = response.xpath('//div[@class="theLogo"]/div/a/text()|//div[@class="hdpHead clearfix"]/div[@class="speNav js_crumb"]/a/text()|//div[@class="w1000"]//div[@class="t-cur"]/a/text()').extract_first()
        if NewsCategorys == '凤凰网科技':
            item['NewsCategory'] = '001.006'
        elif NewsCategorys =='凤凰网资讯':
            item['NewsCategory'] = '001.011'
        elif NewsCategorys == '凤凰网酒业':
            item['NewsCategory'] = '001.039'
        elif NewsCategorys == '凤凰网娱乐':
            item['NewsCategory'] = '001.005'
        elif NewsCategorys == '凤凰网游戏':
            item['NewsCategory'] = '001.016'
        elif NewsCategorys == '警法':
            item['NewsCategory'] = '001.031'
        elif NewsCategorys == '凤凰网汽车':
            item['NewsCategory'] = '001.008'
        elif NewsCategorys == '凤凰网公益':
            item['NewsCategory'] = '001.034'
        elif NewsCategorys == '凤凰网国学':
            item['NewsCategory'] = '001.037'
        elif NewsCategorys == '凤凰网健康':
            item['NewsCategory'] = '001.014'
        elif NewsCategorys == '凤凰网旅游':
            item['NewsCategory'] = '001.017'
        elif NewsCategorys == '凤凰网读书':
            item['NewsCategory'] = '001.026'
        elif NewsCategorys == '凤凰网时尚':
            item['NewsCategory'] = '001.012'
        elif NewsCategorys == '凤凰网财经':
            item['NewsCategory'] = '001.007'
        elif NewsCategorys == '凤凰网文化':
            item['NewsCategory'] = '001.037'
        elif NewsCategorys == '体育':
            item['NewsCategory'] = '001.010'
        elif NewsCategorys == '凤凰网公益':
            item['NewsCategory'] = '001.034'
        elif NewsCategorys == '数码':
            item['NewsCategory'] = '001.024'
        else:
            item['NewsCategory'] = '001.009'
        SourceCategory = response.xpath('//div[@class="theLogo"]/div/a/text()|//div[@class="hdpHead clearfix"]/div[@class="speNav js_crumb"]/a/text()|//div[@class="w1000"]//div[@class="t-cur"]/a/text()').extract_first()
        if SourceCategory is None:
            item['SourceCategory'] = '凤凰新闻'
        else:
            item['SourceCategory'] = '凤凰' + SourceCategory
        item['NewsType'] = 0
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        div_list = response.xpath('//div[@class="main"]/div[@class="left"]')
        for div in div_list:
            NewsTitle = div.xpath('./div/h1/text()').extract()[0]
            SourceName = div.xpath('./div/div[@id="artical_sth"]/p/span/span/a/text()|./div/div[@id="artical_sth"]/p/span/span[@class="ss03"]/text()').extract_first()
            item['AuthorName'] = None
            NewsDates = div.xpath('./div[@id="artical"]/div[@id="artical_sth"]/p/span[@class="ss01"]/text()').extract_first()
            NewsDate = NewsDates.replace('年', '-', 4).replace('月','-').replace('日','')
            item['NewsTitle'] = NewsTitle
            item['SourceName'] = SourceName
            item['NewsDate'] = NewsDate
            img_urls = div.xpath('./div[@id="artical"]/div[@id="artical_real"]/div/p[@class="detailPic"]/img/@src').extract()
            content = ''.join(div.xpath('./div[@id="artical"]/div[@id="artical_real"]/div[@id="main_content"]/p').extract())
            listFiles = []
            client = Fdfs_client('/etc/fdfs/client.conf')
            if len(img_urls) > 0:
                for img_url in img_urls:
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
                        print(a)
                        # b = Decimal(a).quantize(Decimal('0.00'))
                        b = round(float(a),2)
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
                item['NewsContent'] = ''.join(response.xpath('//div[@class="main"]/div[@class="left"]/div[@id="artical"]/div[@id="artical_real"]/div[@id="main_content"]/p').extract())
            item['NewsContent'] = content
            item['FileList'] = listFiles
            yield item
