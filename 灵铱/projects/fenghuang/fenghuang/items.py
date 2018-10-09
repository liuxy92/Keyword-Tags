# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FenghuangItem(scrapy.Item):
    NewsID = scrapy.Field()  # 资讯唯一标示
    NewsCategory = scrapy.Field()  # 资讯大类别
    SourceCategory = scrapy.Field()  # 资讯小类别
    NewsType = scrapy.Field()  # 资讯类型 0-文本，1-图文， 2-视频
    NewsTitle = scrapy.Field()  # 资讯标题
    NewsContent = scrapy.Field()  # 资讯正文内容
    NewsRawUrl = scrapy.Field()  # 资讯正文链接
    SourceName = scrapy.Field()  # 资讯来源（网站名称）
    AuthorName = scrapy.Field()  # 作者名称
    InsertDate = scrapy.Field()  # 入库时间
    NewsDate = scrapy.Field()  # 新闻发布时间
    NewsClickLike = scrapy.Field()  #
    NewsBad = scrapy.Field()  #
    NewsRead = scrapy.Field()  #
    NewsOffline = scrapy.Field()  # 标记新闻是否下线,默认0-上线;1-下线
    FileList = scrapy.Field()
