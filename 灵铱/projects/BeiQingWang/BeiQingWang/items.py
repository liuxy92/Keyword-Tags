# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BeiqingwangItem(scrapy.Item):
    NewsID = scrapy.Field()
    NewsCategory = scrapy.Field()  # 资讯大类别
    SourceCategory = scrapy.Field()  # 资讯小类别
    NewsType = scrapy.Field()  # 资讯类型 0-文本，1-图文， 2-视频
    NewsTitle = scrapy.Field()  # 资讯标题

    NewsContent = scrapy.Field()  # 资讯正文内容

    NewsRawUrl = scrapy.Field()  # 文章的源地址

    SourceName = scrapy.Field()  # 资讯来源（网站名称）

    AuthorName = scrapy.Field()  # 作者名称
    InsertDate = scrapy.Field()  # 入库时间
    image_url = scrapy.Field()  # 图片地址

    NewsDate = scrapy.Field()
    NewsClickLike = scrapy.Field()
    NewsBad = scrapy.Field()
    NewsRead = scrapy.Field()
    NewsOffline = scrapy.Field()
    FileList = scrapy.Field()
