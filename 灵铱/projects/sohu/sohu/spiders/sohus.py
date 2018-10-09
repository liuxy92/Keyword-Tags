# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from sohu.items import SohuItem
import uuid
import requests
from hashlib import md5
import re
import datetime
from fdfs_client.client import *
from requests.exceptions import ConnectionError
from decimal import *
class SohusSpider(CrawlSpider):
    name = 'sohus'
    # allowed_domains = ['news.sohu.com']
    start_urls = ['http://news.sohu.com/']

    rules = (
        Rule(LinkExtractor(allow=r'(\w+).sohu.com/$',deny=r'(\w+).blog.sohu.com'), follow=True),
        Rule(LinkExtractor(allow=r'/a/(\d+)_(\d+)'), callback='parse_item', follow=False),
    )
    def parse_item(self, response):
        item = SohuItem()
        item['NewsRawUrl'] = response.url
        item['NewsID'] = str(uuid.uuid1())
        NewsCategorys = response.xpath('//div[@class="location area"]/a/text()').extract()[0]
        if NewsCategorys == '科技':
            item['NewsCategory'] = '001.006'
        elif NewsCategorys == '体育':
            item['NewsCategory'] = '001.010'
        elif NewsCategorys == '社会':
            item['NewsCategory'] = '001.009'
        elif NewsCategorys == '动漫':
            item['NewsCategory'] = '001.030'
        elif NewsCategorys == '游戏':
            item['NewsCategory'] = '001.016'
        elif NewsCategorys == '警法':
            item['NewsCategory'] = '001.031'
        elif NewsCategorys == '汽车':
            item['NewsCategory'] = '001.008'
        elif NewsCategorys == '宠物':
            item['NewsCategory'] = '001.032'
        elif NewsCategorys == '搞笑':
            item['NewsCategory'] = '001.033'
        elif NewsCategorys == '公益':
            item['NewsCategory'] = '001.034'
        elif NewsCategorys == '娱乐':
            item['NewsCategory'] = '001.005'
        elif NewsCategorys == '星座':
            item['NewsCategory'] = '001.035'
        elif NewsCategorys == '军事':
            item['NewsCategory'] = '001.011'
        elif NewsCategorys == '文化':
            item['NewsCategory'] = '001.037'
        elif NewsCategorys == '历史':
            item['NewsCategory'] = '001.038'
        elif NewsCategorys == '母婴':
            item['NewsCategory'] = '001.018'
        elif NewsCategorys == '健康':
            item['NewsCategory'] = '001.014'
        elif NewsCategorys == '美食':
            item['NewsCategory'] = '001.036'
        elif NewsCategorys == '旅游':
            item['NewsCategory'] = '001.017'
        elif NewsCategorys == '教育':
            item['NewsCategory'] = '001.026'
        elif NewsCategorys == '时尚':
            item['NewsCategory'] = '001.012'
        elif NewsCategorys == '财经':
            item['NewsCategory'] = '001.007'
        elif NewsCategorys == '星座':
            item['NewsCategory'] = '001.035'
        div_list = response.xpath('//div[@class="area clearfix"]/div[@class="left main"]/div[@class="text"]')
        for div in div_list:
            SourceCategory = div.xpath('./div[@class="text-title"]/div/span[@class="tag"]/a/text()').extract_first()
            if SourceCategory is None:
                item['SourceCategory'] = '搜狐新闻'
            else:
                item['SourceCategory'] = '搜狐' + SourceCategory
            item['NewsType'] = 0
            NewsTitle = div.xpath('./div/h1/text()').extract()[0]
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
            img_urls = div.xpath('.//p/img/@src').extract()
            content = ''.join(div.xpath('.//p').extract())
            listFiles = []
            client = Fdfs_client('/etc/fdfs/client.conf')
            if len(img_urls) > 0:
                for img_url in img_urls:
                    print(img_urls)
                    if 'http' in img_url:
                        img_url = img_url
                        print(2345)
                    else:
                        img_url = 'http:' + img_url
                        print(1234)
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
                        b = round(float(a),2)
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
                item['NewsContent'] = ''.join(div.xpath('./article[@class="article"]/p').extract_first())
            item['NewsContent'] = content
            item['FileList'] = listFiles
            yield item