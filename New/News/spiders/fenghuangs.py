# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from News.items import NewsItem
import uuid,re
import requests
from hashlib import md5
from News.file_model import File_mod
from fdfs_client.client import *
class FenghuangsSpider(CrawlSpider):
    name = 'fenghuangs'
    allowed_domains = ['ifeng.com']
    start_urls = ['http://news.ifeng.com/']

    rules = (
        Rule(LinkExtractor(allow=r'(\w+).ifeng.com/$'), follow=True),
        Rule(LinkExtractor(allow=r'(\w+).ifeng.com/a/2018[0-9]{4}/(\d+)_\d\.shtml'), callback='parse_item', follow=False),
    )
    custom_settings = {
        "COOKIES_ENABLED": True
    }
    def parse_item(self, response):
        # print(response.url)
        item = NewsItem()
        item['NewsRawUrl'] = response.url
        i = datetime.datetime.now()
        b = "%s0%s" % (i.year, i.month)
        item['NewsID'] = '{0}-'.format(b) + str(uuid.uuid1())
        NewsCategorys = response.xpath('//div[@class="theLogo"]/div/a/text()|//div[@class="hdpHead clearfix"]/div[@class="speNav js_crumb"]/a/text()|//div[@class="w1000"]//div[@class="t-cur"]/a/text()').extract_first()
        if NewsCategorys == '凤凰网科技':
            item['NewsCategory'] = '001.006'
        elif NewsCategorys =='凤凰网资讯':
            item['NewsCategory'] = '001.011'
        elif NewsCategorys == '凤凰网酒业':
            item['NewsCategory'] = '001.038'
        elif NewsCategorys == '凤凰网娱乐':
            item['NewsCategory'] = '001.005'
        elif NewsCategorys == '凤凰网游戏':
            item['NewsCategory'] = '001.016'
        elif NewsCategorys == '警法':
            item['NewsCategory'] = '001.030'
        elif NewsCategorys == '凤凰网汽车':
            item['NewsCategory'] = '001.008'
        elif NewsCategorys == '凤凰网公益':
            item['NewsCategory'] = '001.033'
        elif NewsCategorys == '凤凰网国学':
            item['NewsCategory'] = '001.036'
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
            item['NewsCategory'] = '001.036'
        elif NewsCategorys == '体育':
            item['NewsCategory'] = '001.010'
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
        image_urls = response.xpath('//div[@id="main_content"]/p/img/@src').extract()
        content = ''.join(response.xpath('//div[@id="main_content"]/p').extract())
        listFiles = []
        if len(image_urls) > 0:
            for image_url in image_urls:
                response_url = response.url
                a = File_mod(image_url, content,response_url)
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
