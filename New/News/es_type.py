# -*- coding:utf-8 -*-

from elasticsearch_dsl import DocType,Nested,Date,Boolean,analyzer,Completion,Text,Keyword,Integer
from elasticsearch_dsl.connections import connections

# 新建连接
connections.create_connection(hosts="10.100.101.172")


class ArticleType(DocType):
    # 文章类型
    NewsID = Keyword()
    NewsCategory = Keyword()
    SourceCategory = Keyword()
    NewsType = Integer()
    NewsTitle = Keyword()
    NewsContent = Keyword()
    NewsRawUrl = Keyword()
    SourceName = Keyword()
    InsertDate = Date()

    class Meta:
        # 数据库名称和表名称
        index = "im_news"
        doc_type = "tbl_NewsDetails"


if __name__ == '__main__':
    ArticleType.init()
