# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from wangyi.items import WangyiItem
import uuid
import requests
from hashlib import md5
import re
import datetime
from fdfs_client.client import *
from requests.exceptions import ConnectionError
from decimal import *
class WangyisSpider(CrawlSpider):
    name = 'wangyis'
    # allowed_domains = ['wangyi.com']
    start_urls = ['http://news.163.com/']

    rules = (
        Rule(LinkExtractor(allow=r'http://(\w+).163.com$'),follow=True),
        Rule(LinkExtractor(allow=r'(\w+).[1-9]{3}.com/18/[0-9]{4}/[0-9]{2}/(\w+).html$',deny=r'vhouse.[1-9]{3}.com' ), callback='parse_item',follow=True),
    )
    def parse_item(self, response):
        item = WangyiItem()
        item['NewsRawUrl'] = response.url
        item['NewsID'] = str(uuid.uuid1())
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
            item['NewsCategory'] = '001.029'
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
        print(type(AuthorNames))
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
        img_urls = response.xpath('//div[@class="post_text"]/p[@class="f_center"]/img/@src').extract()
        content = ''.join(response.xpath('//div[@class="post_text"]/p|//div[@class="post_text"]/div[@class="ArticleContent"]/p').extract())
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
            item['NewsContent'] = ''.join(response.xpath('//div[@class="post_text"]/p | //div[@class="post_text"]/div[@class="ArticleContent"]/p').extract())
        item['NewsContent'] = content
        item['FileList'] = listFiles
        yield item