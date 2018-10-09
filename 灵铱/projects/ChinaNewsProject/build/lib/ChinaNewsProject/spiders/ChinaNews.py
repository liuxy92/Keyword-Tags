# -*- coding: utf-8 -*-
import scrapy
import uuid
import time
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import ChinanewsprojectItem
from ..file_model import File_mod

class ChinanewsSpider(CrawlSpider):
    name = 'ChinaNews'
    # allowed_domains = ['www.chinanews.com']
    start_urls = ['http://www.chinanews.com/']

    rules = (
        Rule(LinkExtractor(allow=r'/scroll-news/news\d+\.html'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        div_list = response.xpath('//div[@id="content"]/div[@id="content_right"]/div[@class="content_list"]/ul/li')
        for div in div_list:
            item = ChinanewsprojectItem()
            item['NewsID'] = str(uuid.uuid1())
            # 资讯大类别
            NewsCategory = div.xpath('./div[@class="dd_lm"]/a/text()').extract_first()
            if NewsCategory == '体育':
                item['NewsCategory'] = '001.010'
                item['NewsTitle'] = div.xpath('./div[@class="dd_bt"]/a/text()').extract_first()
                link = div.xpath('./div[@class="dd_bt"]/a/@href').extract_first()
                yield scrapy.Request(url='http://' + str(link), callback=self.parse_info, meta={'item': item})
            if NewsCategory == '军事':
                item['NewsCategory'] = '001.011'
                item['NewsTitle'] = div.xpath('./div[@class="dd_bt"]/a/text()').extract_first()
                link = div.xpath('./div[@class="dd_bt"]/a/@href').extract_first()
                yield scrapy.Request(url='http://' + str(link), callback=self.parse_info, meta={'item': item})
            if NewsCategory == '社会':
                item['NewsCategory'] = '001.009'
                item['NewsTitle'] = div.xpath('./div[@class="dd_bt"]/a/text()').extract_first()
                link = div.xpath('./div[@class="dd_bt"]/a/@href').extract_first()
                yield scrapy.Request(url='http://' + str(link), callback=self.parse_info, meta={'item': item})
            if NewsCategory == '财经':
                item['NewsCategory'] = '001.007'
                item['NewsTitle'] = div.xpath('./div[@class="dd_bt"]/a/text()').extract_first()
                link = div.xpath('./div[@class="dd_bt"]/a/@href').extract_first()
                yield scrapy.Request(url='http://' + str(link), callback=self.parse_info, meta={'item': item})
            if NewsCategory == '国际':
                item['NewsCategory'] = '001.020'
                item['NewsTitle'] = div.xpath('./div[@class="dd_bt"]/a/text()').extract_first()
                links = div.xpath('./div[@class="dd_bt"]/a/@href').extract()
                for link in links:
                    if 'www.chinanews.com/gj/shipin/' in link:
                        return None
                    if 'www.chinanews.com/shipin/' in link:
                        return None
                    else:
                        yield scrapy.Request(url='http://' + str(link), callback=self.parse_info, meta={'item': item})
            if NewsCategory == '娱乐':
                item['NewsCategory'] = '001.005'
                item['NewsTitle'] = div.xpath('./div[@class="dd_bt"]/a/text()').extract_first()
                link = div.xpath('./div[@class="dd_bt"]/a/@href').extract_first()
                yield scrapy.Request(url='http://' + str(link), callback=self.parse_info, meta={'item': item})
            if NewsCategory == '游戏':
                item['NewsCategory'] = '001.016'
                item['NewsTitle'] = div.xpath('./div[@class="dd_bt"]/a/text()').extract_first()
                link = div.xpath('./div[@class="dd_bt"]/a/@href').extract_first()
                yield scrapy.Request(url='http://' + str(link), callback=self.parse_info, meta={'item': item})
            if NewsCategory == '汽车':
                item['NewsCategory'] = '001.008'
                item['NewsTitle'] = div.xpath('./div[@class="dd_bt"]/a/text()').extract_first()
                link = div.xpath('./div[@class="dd_bt"]/a/@href').extract_first()
                yield scrapy.Request(url='http://' + str(link), callback=self.parse_info, meta={'item': item})
            else:
                pass


    def parse_info(self, response):
        print(response.url)
        item = response.meta['item']
        item['SourceCategory'] = 'chinanews' + str(response.xpath('//div[@id="nav_div980"]/div[@id="nav"]/a[2]/text()').extract_first())
        item['NewsType'] = 0
        item['NewsRawUrl'] = response.url
        data = response.xpath('//div[@class="left-time"]/div[@class="left-t"]/a[2]/text()').extract_first()
        if data == '参与互动':
            item['SourceName'] = response.xpath('//div[@class="left-time"]/div[@class="left-t"]/a[1]/text()').extract_first()
            item['NewsDate'] = response.xpath('//div[@class="left-time"]/div[@class="left-t"]/text()').extract_first()[:-3].strip().replace('年', '-').replace('月', '-').replace('日', '') + ':00'
        else:
            try:
                item['SourceName'] = response.xpath('//div[@class="left-time"]/div[@class="left-t"]/text()').extract_first()[22:]
                item['NewsDate'] = response.xpath('//div[@class="left-time"]/div[@class="left-t"]/text()').extract_first()[:19].strip().replace('年', '-').replace('月', '-').replace('日', '') + ':00'
            except Exception as e:
                print(e)
        item['AuthorName'] = response.xpath('//div[@class="left_name"]/div[@class="left_name"]/text()').extract_first()[5:][:-2]
        item['InsertDate'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        item['NewsClickLike'] = 0
        item['NewsBad'] = 0
        item['NewsRead'] = 0
        item['NewsOffline'] = 0

        # 获取图片链接
        image_urls = response.xpath(
            '//div[@class="content"]/div[@class="left_zw"]/div//img/@src | //div[@class="content"]/div[@class="left_zw"]/p//img/@src').extract()
        content = ''.join(
            response.xpath('//div[@class="content"]/div[@class="left_zw"]/div | //div[@class="content"]/div[@class="left_zw"]/p').extract())
        listFiles = []
        if image_urls is not None:
            for image_url in image_urls:
                a = File_mod(image_url, content)
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
        else:
            item['NewsContent'] = ''.join(
                response.xpath(
                    '//div[@class="content"]/div[@class="left_zw"]/div | //div[@class="content"]/div[@class="left_zw"]/p').extract())
        item['NewsContent'] = content
        item['FileList'] = listFiles

        yield item


