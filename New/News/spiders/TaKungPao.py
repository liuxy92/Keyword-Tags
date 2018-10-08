# -*- coding: utf-8 -*-
import scrapy
import time,datetime,uuid,os,requests

from ..file_model import File_mod
from ..items import NewsItem

class TakungpaoSpider(scrapy.Spider):
    name = 'TaKungPao'
    # allowed_domains = ['www']
    start_urls = [
        'http://news.takungpao.com/world/exclusive/',
        'http://finance.takungpao.com/roll/',
    ]

    def parse(self, response):
        div_list = response.xpath('//div[@class="txtImgList clearfix"]/div')
        for div in div_list:
            link = div.xpath('./h3/a/@href').extract_first()

            yield scrapy.Request(link, self.parse_info)

        # 获取下页链接
        next = response.xpath('//div[@class="page"]/div//a[last()]/@href').extract_first()
        if next:
            if next.split('/index')[1] == '_2.html' or next.split('/index')[1] == '_3.html':

                yield scrapy.Request(next, self.parse)

    def parse_info(self, response):
        item = NewsItem()
        i = datetime.datetime.now()
        b = "%s0%s" % (i.year, i.month)
        item['NewsID'] = '{0}-'.format(b) + str(uuid.uuid1())
        link = response.url.split('.takungpao.com')
        if 'http://news' == link[0]:
            item['NewsCategory'] = '001.020'  # 国际
            item['SourceCategory'] = '大公国际'
        elif 'http://finance' == link[0]:
            item['NewsCategory'] = '001.007'  # 财经
            item['SourceCategory'] = '大公财经'
        item['NewsType'] = 0
        item['NewsRawUrl'] = response.url
        item['NewsTitle'] = response.xpath('//div[@class="tpk_con clearfix"]/h1/text()').extract_first()
        # 文章来源
        name = response.xpath('//div[@class="fl_dib"][2]/a/text()').extract_first()
        if name is None:
            SourceName = response.xpath('//div[@class="fl_dib"][2]/text()').extract_first()[3:]
            item['SourceName'] = SourceName
        else:
            item['SourceName'] = name
        # 作者
        item['AuthorName'] = response.xpath('//div[@class="tkp_con_author clearfix"]/span/text()').extract_first()[5:8]
        item['InsertDate'] = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
        item['NewsDate'] = response.xpath('//div[@class="fl_dib"][1]/text()').extract_first()
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0

        # 获取图片链接
        image_urls = response.xpath(
            '//div[@class="tpk_con clearfix"]/div[@class="tpk_text clearfix"]/p//img/@src | '
            '//div[@class="tpk_text clearfix"]/div/p/img/@src'
        ).extract()
        try:
            content = ''.join(
                response.xpath(
                    '//div[@class="tpk_con clearfix"]/div[@class="tpk_text clearfix"]/p |'
                    '//div[@class="tpk_text clearfix"]/div/p'
                ).extract())
        except:
            content = 'None'
        listFiles = []
        if image_urls:
            for image_url in image_urls:
                if '?' in image_url:
                    image_url_new = image_url.split('?')[0]
                else:
                    image_url_new = image_url
                a = File_mod(image_url_new, content)
                content = a.detail_file()
                if 'v1' in image_url:
                    full_name = a.Download_video()
                else:
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
        item['NewsContent'] = content
        item['FileList'] = listFiles

        yield item
