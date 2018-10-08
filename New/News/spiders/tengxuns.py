# -*- coding: utf-8 -*-
import scrapy
from News.items import NewsItem
import uuid,datetime,time,re,requests
from fdfs_client.client import *
from News.file_model import File_mod
class TengxunsSpider(scrapy.Spider):
    name = 'tengxuns'
    # allowed_domains = ['qq.com']
    start_urls =[
                 'http://finance.qq.com/',
                 'http://sports.qq.com/',
                 'http://ent.qq.com/',
                 'http://www.jia360.com/new/',
                 'http://digi.tech.qq.com/hea/',
                 'http://tech.qq.com/',
                 'http://digi.tech.qq.com/',
                 'http://digi.tech.qq.com/mobile/',
                 'http://games.qq.com/',
                 'http://edu.qq.com/',
                 'http://cul.qq.com/',
    ]
    custom_settings = {
        "COOKIES_ENABLED": True
    }
    def parse(self, response):
        print(response.url)
        item = NewsItem()
        if 'http://finance.qq.com/' in response.url:
            item['NewsCategory'] = '001.007'
        elif 'http://news.qq.com/photo.shtml' in response.url:
            item['NewsCategory'] = '001.004'
        elif 'http://sports.qq.com/' in response.url:
            item['NewsCategory'] = '001.010'
        elif 'http://ent.qq.com/' in response.url:
            item['NewsCategory'] = '001.005'
        elif 'http://fashion.qq.com/' in response.url:
            item['NewsCategory'] = '001.012'
        elif 'http://baby.qq.com/' in response.url:
            item['NewsCategory'] = '001.018'
        elif 'http://auto.qq.com/' in response.url:
            item['NewsCategory'] = '001.008'
        elif 'http://www.jia360.com/' in response.url:
            item['NewsCategory'] = '001.025'
        elif 'http://digi.tech.qq.com/hea/' in response.url:
            item['NewsCategory'] = '001.028'
        elif 'http://tech.qq.com/' in response.url:
            item['NewsCategory'] = '001.006'
        elif 'http://digi.tech.qq.com/' in response.url:
            item['NewsCategory'] = '001.024'
        elif 'http://digi.tech.qq.com/mobile/' in response.url:
            item['NewsCategory'] = '001.023'
        elif 'http://games.qq.com/' in response.url:
            item['NewsCategory'] = '001.016'
        elif 'http://astro.fashion.qq.com/' in response.url:
            item['NewsCategory'] = '001.034'
        elif 'http://edu.qq.com/' in response.url:
            item['NewsCategory'] = '001.026'
        elif 'http://cul.qq.com/' in response.url:
            item['NewsCategory'] = '001.036'
        else:
            return None

        links = response.xpath('//div[@class="Q-tpList"]/div/a/@href|'
                               '//div[@class="fl"]/ul/li/span/a/@href|'
                               '//div[@class="mod_txt"]/h3/a/@href|'
                               '//li[@class="li1"]/a/@href|'
                               '//div[@class="info"]/h3/a/@href|'
                               '//div[@class="article single"]/div[@class="title"]/a/@href|'
                               '//div[@class="Q-tpList"]/div[@class="content"]/em/a/@href').extract()
        for link in links:
            if '//' not in link:
                link = 'http://sports.qq.com' + link
                # link = 'http:' + link
            elif 'http' not in link:
                # link = 'http://sports.qq.com' + link
                link = 'http:' + link
            else:
                link = link
            yield scrapy.Request(link,meta={'item': item},callback=self.parse_detail)
    def parse_detail(self,response):
        item = response.meta['item']
        item['NewsRawUrl'] = response.url
        i = datetime.datetime.now()
        b = "%s0%s" % (i.year, i.month)
        item['NewsID'] = '{0}-'.format(b) + str(uuid.uuid1())
        SourceCategory = response.xpath('//span[@class="a_source"]/text()|'
                                        '//span[@class="a_source"]/a/text()|'
                                        '//div[@class="time"]/span/text()|'
                                        '//div[@class="top1"]/h1/text()').extract()
        if len(SourceCategory) == 0:
            item['SourceCategory'] = '腾讯新闻'
        else:
            SourceCategory = ''.join(SourceCategory)
            item['SourceCategory'] = '腾讯新闻' + SourceCategory
        item['NewsType'] = 0
        NewsTitle = response.xpath('//div[@class="qq_conent clearfix"]/div[@class="LEFT"]/h1/text()|'
                                   '//div[@class="hd"]/h1/text()|'
                                   '//div[@class="title"]/h1/text()|'
                                   '//div[@class="fl newsD_left"]/h6/text()').extract_first()
        if not NewsTitle is None:
            item['NewsTitle'] = NewsTitle
        else:
            pass
        item['SourceName'] = '腾讯网'
        item['AuthorName'] = 'None'
        NewsDate = re.findall('<meta name="_pubtime" content="(.*?)">',response.text)
        if len(NewsDate) == 0:
            NewsDates = response.xpath('//span[@class="a_time"]/text()').extract()
            if len(NewsDates) == 1:
                item['NewsDate'] = NewsDates
            elif len(NewsDates) > 1:
                NewsDates = response.xpath('//div[@class="time"]/span/text()').extract()[1]
                item['NewsDate'] = NewsDates
            else:
                item['NewsDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        else:
            item['NewsDate'] = NewsDate
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0
        image_urls = response.xpath('//p[@class="one-p"]/img/@src|'
                                    '//div[@id="Cnt-Main-Article-QQ"]/p/img/@src|'
                                    '//div[@class="newsD_contend"]/p/img/@src|'
                                    '//div[@class="content-article"]/p/img/@src').extract()
        if len(image_urls) == 0:
            print(response.url, 222222222222222222)
        # content = ''.join(response.xpath('//p[@class="one-p"]').extract())
        content = ''.join(response.xpath(
                                 '//div[@id="Cnt-Main-Article-QQ"]/p|'
                                 '//div[@class="newsD_contend"]/p|'
                                 '//div[@class="content-article"]/p').extract())
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
                content = content.replace(i,'')
                item['NewsContent'] = content
        else:
            item['NewsContent'] = content
        item['FileList'] = listFiles
        yield item



