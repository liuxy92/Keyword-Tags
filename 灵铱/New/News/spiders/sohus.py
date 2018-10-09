# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from News.items import NewsItem
import uuid,re
from News.file_model import File_mod
from fdfs_client.client import *
from requests.exceptions import ConnectionError
from decimal import *
from urllib.parse import urljoin
class SohusSpider(CrawlSpider):
    name = 'sohus'
    # allowed_domains = ['news.sohu.com']
    start_urls = ['http://news.sohu.com/']

    rules = (
        Rule(LinkExtractor(allow=r'(\w+).sohu.com/$',deny=r'(\w+).blog.sohu.com'), follow=True),
        Rule(LinkExtractor(allow=r'/a/(\d+)_(\d+)'), callback='parse_item', follow=False),
    )
    def parse_item(self, response):
        item = NewsItem()
        item['NewsRawUrl'] = response.url
        i = datetime.datetime.now()
        b = "%s0%s" % (i.year, i.month)
        item['NewsID'] = '{0}-'.format(b) + str(uuid.uuid1())
        NewsCategorys = response.xpath('//div[@class="location area"]/a/text()').extract()[0]
        if NewsCategorys == '科技':
            item['NewsCategory'] = '001.006'
        elif NewsCategorys == '体育':
            item['NewsCategory'] = '001.010'
        elif NewsCategorys == '社会':
            item['NewsCategory'] = '001.009'
        elif NewsCategorys == '动漫':
            item['NewsCategory'] = '001.029'
        elif NewsCategorys == '游戏':
            item['NewsCategory'] = '001.016'
        elif NewsCategorys == '警法':
            item['NewsCategory'] = '001.030'
        elif NewsCategorys == '汽车':
            item['NewsCategory'] = '001.008'
        elif NewsCategorys == '宠物':
            item['NewsCategory'] = '001.031'
        elif NewsCategorys == '搞笑':
            item['NewsCategory'] = '001.032'
        elif NewsCategorys == '公益':
            item['NewsCategory'] = '001.033'
        elif NewsCategorys == '娱乐':
            item['NewsCategory'] = '001.005'
        elif NewsCategorys == '星座':
            item['NewsCategory'] = '001.034'
        elif NewsCategorys == '军事':
            item['NewsCategory'] = '001.011'
        elif NewsCategorys == '文化':
            item['NewsCategory'] = '001.036'
        elif NewsCategorys == '历史':
            item['NewsCategory'] = '001.037'
        elif NewsCategorys == '母婴':
            item['NewsCategory'] = '001.018'
        elif NewsCategorys == '健康':
            item['NewsCategory'] = '001.014'
        elif NewsCategorys == '美食':
            item['NewsCategory'] = '001.035'
        elif NewsCategorys == '旅游':
            item['NewsCategory'] = '001.017'
        elif NewsCategorys == '教育':
            item['NewsCategory'] = '001.026'
        elif NewsCategorys == '时尚':
            item['NewsCategory'] = '001.012'
        elif NewsCategorys == '财经':
            item['NewsCategory'] = '001.007'
        div_list = response.xpath('//div[@class="area clearfix"]/div[@class="left main"]/div[@class="text"]')
        for div in div_list:
            SourceCategory = div.xpath('./div[@class="text-title"]/div/span[@class="tag"]/a/text()').extract_first()
            if SourceCategory is None:
                item['SourceCategory'] = '搜狐新闻'
            else:
                item['SourceCategory'] = '搜狐' + SourceCategory
            item['NewsType'] = 0
            NewsTitle = div.xpath('./div/h1/text()').extract()[0]
            print(NewsTitle)
            SourceName = div.xpath('.//div[@class="article-info"]/span[@data-role="original-link"]/a/text()').extract()[0]
            item['NewsTitle'] = NewsTitle
            item['SourceName'] = SourceName
            item['AuthorName'] = None
            item['NewsDate'] = div.xpath('./div[@class="text-title"]/div/span[@id="news-time"]/text()').extract()[0]
            item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            item['NewsClickLike'] = 0
            item['NewsBad'] = 0
            item['NewsRead'] = 0
            item['NewsOffline'] = 0

        content = ''.join(response.xpath('//article[@class="article"]/p').extract())
        image_urls = response.xpath('//article[@class="article"]/p/img/@src').extract()
        listFiles = []
        if self.settings.get('OPEN') == 1:
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
        else:
            if len(image_urls) > 0:
                for image_url in image_urls:
                    if image_url.startswith('//'):
                        response_url = response.url
                        image_after = urljoin(response_url, image_url)
                        filemodel = {}
                        filemodel['FileID'] = str(uuid.uuid1())
                        filemodel['FileType'] = 0
                        filemodel['FileDirectory'] = image_after
                        filemodel['FileDirectoryCompress'] = None
                        filemodel['FileDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        filemodel['FileLength'] = None
                        filemodel['FileUserID'] = None
                        filemodel['Description'] = None
                        filemodel['NewsID'] = item['NewsID']
                        filemodel['image_url'] = image_after
                        listFiles.append(filemodel)
                    else:
                        filemodel = {}
                        filemodel['FileID'] = str(uuid.uuid1())
                        filemodel['FileType'] = 0
                        filemodel['FileDirectory'] = image_url
                        filemodel['FileDirectoryCompress'] = None
                        filemodel['FileDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        filemodel['FileLength'] = None
                        filemodel['FileUserID'] = None
                        filemodel['Description'] = None
                        filemodel['NewsID'] = item['NewsID']
                        filemodel['image_url'] = image_url
                        listFiles.append(filemodel)
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
