# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from News.items import NewsItem
import uuid
from decimal import *
import re
from fdfs_client.client import *
from News.file_model import File_mod
class WangyisSpider(CrawlSpider):
    name = 'wangyis'
    # allowed_domains = ['wangyi.com']
    start_urls = ['http://news.163.com/']

    rules = (
        Rule(LinkExtractor(allow=r'http://(\w+).163.com$'),follow=True),
        Rule(LinkExtractor(allow=r'(\w+).[1-9]{3}.com/18/[0-9]{4}/[0-9]{2}/(\w+).html$',deny=r'vhouse.[1-9]{3}.com' ), callback='parse_item',follow=True),
    )
    custom_settings = {
        "COOKIES_ENABLED": True
    }
    def parse_item(self, response):
        item = NewsItem()
        item['NewsRawUrl'] = response.url
        i = datetime.datetime.now()
        b = "%s0%s" % (i.year, i.month)
        item['NewsID'] = '{0}-'.format(b) + str(uuid.uuid1())
        NewsCategorys=response.xpath('//div[@class="clearfix"]/div[@class="post_crumb"]/a/text()').extract()[1]
        if NewsCategorys == '体育频道':
            item['NewsCategory'] = '001.010'
        elif NewsCategorys == '网易娱乐':
            item['NewsCategory'] = '001.005'
        elif NewsCategorys == '财经频道':
            item['NewsCategory'] = '001.007'
        elif NewsCategorys == '汽车频道':
            item['NewsCategory'] = '001.008'
        elif NewsCategorys == '网易科技':
            item['NewsCategory'] = '001.006'
        elif NewsCategorys == '网易手机':
            item['NewsCategory'] = '001.023'
        elif NewsCategorys == '数码频道':
            item['NewsCategory'] = '001.024'
        elif NewsCategorys == '女人频道':
            item['NewsCategory'] = '001.012'
        elif NewsCategorys == '网易家居':
            item['NewsCategory'] = '001.025'
        elif NewsCategorys == '教育频道':
            item['NewsCategory'] = '001.026'
        elif NewsCategorys == '健康频道':
            item['NewsCategory'] = '001.014'
        elif NewsCategorys == '艺术频道':
            item['NewsCategory'] = '001.027'
        elif NewsCategorys == '家电频道':
            item['NewsCategory'] = '001.028'
        else:
            print('无类别')
        SourceCategory = response.xpath('//div[@class="clearfix"]/div[@class="post_crumb"]/a/text()').extract()[1]
        if SourceCategory is not None:
            item['SourceCategory'] = '网易' + str(SourceCategory)
        else:
            item['SourceCategory'] = '网易新闻'
        item['NewsType'] = 0
        NewsTitles = response.xpath('//div[@class="post_content post_area clearfix"]/div[@class="post_content_main"]/h1/text()').extract()
        if len(NewsTitles) == 0:
            pass
        else:
            item['NewsTitle'] = response.xpath('//div[@class="post_content post_area clearfix"]/div[@class="post_content_main"]/h1/text()').extract_first()
        SourceNames = response.xpath('//div[@class="post_content post_area clearfix"]/div[@class="post_content_main"]/div[@class="post_time_source"]/a[@id="ne_article_source"]/text()').extract()
        if len(SourceNames) == 0:
            item['SourceName'] = '网易新闻'
        else:
            item['SourceName'] = response.xpath('//div[@class="post_content post_area clearfix"]/div[@class="post_content_main"]/div[@class="post_time_source"]/a[@id="ne_article_source"]/text()').extract_first()
        AuthorNames = response.xpath('//div[@class="post_text"]/div[@class="ep-source cDGray"]/span[@class="ep-editor"]/text()|//div[@class="end-text"]/div[@class="ep-source cDGray"]/span[@class="ep-editor"]/text()').extract_first()
        b = r'责任编辑：(.*)_'
        AuthorNames = re.findall(b,AuthorNames)
        AuthorName =''.join(AuthorNames)
        item['AuthorName'] = AuthorName
        NewsDatess= response.xpath('//div[@class="post_content post_area clearfix"]/div[@class="post_content_main"]/div[@class="post_time_source"]/text()').extract_first()
        NewsDates = NewsDatess.strip()
        item['NewsDate'] = NewsDates.replace('来源:','')
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        content = ''.join(response.xpath("//div[@id='endText']/p").extract())
        a = re.compile(r'<img .*?src="(.*?)"')
        image_urls = a.findall(content)
        print(image_urls)
        print(content)
        listFiles = []
        if len(image_urls) > 0:
            for image_url in image_urls:
                response_url = response.url
                a = File_mod(image_url, content, response_url)
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
                content = content.replace(i, '')
                item['NewsContent'] = content
        else:
            item['NewsContent'] = content
        item['FileList'] = listFiles
        yield item