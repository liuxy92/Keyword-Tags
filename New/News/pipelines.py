# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import redis
import pymysql,datetime
from twisted.enterprise import adbapi
import pymysql.cursors
import base64
from DBUtils.PooledDB import PooledDB
import io
import sys,json
from scrapy.exceptions import DropItem
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

# elasticsearch服务器
from elasticsearch import Elasticsearch


class NewsPipeline(object):
    def __init__(self):
        print('连接redis')
        self.red = redis.Redis(host="172.18.113.100", port=6379, db=2, decode_responses=True)
        # self.red = redis.Redis(host="127.0.0.1", port=6379, db=2, decode_responses=True)
        print('连接成功')
        print('连接mysql服务器')
        db_config = {"host": '172.18.115.15', "port": 3306, "user": 'Dev3', "passwd": '123456', "db": 'Im',
                     "charset": 'utf8'}
        # db_config = {"host": '127.0.0.1', "port": 3306, "user": 'root', "passwd": '123456', "db": 'sys',
        #              "charset": 'utf8'}
        self.pool = PooledDB(pymysql, 5, **db_config)
        # 5为连接池里的最少连接数
        self.conn = self.pool.connection()
        # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            # 获取redis所有为NewsTitle的key值
            keys = self.red.keys('NewsTitle')
            # 转变类型为字符串
            key = ''.join(keys)
            # lrange获取所有key值为NewsTitle的内容
            value = self.red.lrange('%s' % key, '0', '-1')
            # 判断内容是否为空
            if len(value) >= 0:
                NewsTitless = base64.b64encode(item['NewsTitle'].encode('utf-8'))
                NewsTitles = str(NewsTitless, 'utf-8')
                # 判断爬取的title是否在redis key值为NewsTitle里在提示已存在，不在执行添加
                if NewsTitles not in value:
                    if item['NewsTitle'] == '' or item['NewsContent'] == '' or item['NewsContent'] == '':
                        pass
                    else:
                        i = datetime.datetime.now()
                        b = "%s0%s" % (i.year, i.month)
                        self.red.lpush('NewsTitle', base64.b64encode(item['NewsTitle'].encode('utf-8')))
                        sql1 = 'insert ignore into tbl_NewsDetails{0}(NewsID, NewsCategory, SourceCategory, NewsType, NewsTitle, NewsRawUrl, SourceName, InsertDate, NewsContent, NewsDate, NewsClickLike, NewsBad, NewsRead, NewsOffline)' \
                               'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'.format(b)
                        sql2 = 'insert into tbl_NewsFileManager{0}(FileID, FileType, FileDirectory, FileDirectoryCompress, FileDate, FileLength, FileUserID, Description, NewsID,image_url)' \
                               'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'.format(b)
                        try:
                            self.cur.execute(sql1, (
                                item['NewsID'], item["NewsCategory"], item["SourceCategory"], item["NewsType"],
                                item["NewsTitle"],
                                item["NewsRawUrl"], item["SourceName"], item["InsertDate"], item["NewsContent"],
                                item['NewsDate'], item['NewsClickLike'], item['NewsBad'], item['NewsRead'],
                                item['NewsOffline']
                            ))
                            for dic in item['FileList']:
                                self.cur.execute(sql2, (
                                    dic['FileID'], dic["FileType"], dic["FileDirectory"],
                                    dic["FileDirectoryCompress"],
                                    dic["FileDate"],
                                    dic["FileLength"], dic["FileUserID"], dic["Description"], dic["NewsID"],
                                    dic["image_url"]
                                ))
                            self.conn.commit()
                        except Exception as e:
                            print(e)
                            print("执行sql语句失败")
                        items = json.dumps(dict(item))
                        self.red.lpush(b + 'news' + item['NewsCategory'], items)
                        return item
                else:
                    print('redis数据已存在')
            else:
                print('出错')
        except:
            print('错误操作')
    def close_conn(self, spider):
        # 关闭链接
        self.conn.close()
        # 关闭游标
        self.cur.close()


class ElasticsearchPipeline(object):
    def __init__(self):
        # 连接elasticsearch,默认是9200
        self.es = Elasticsearch(['10.100.101.172:9200'])

    # 将数据写入到es中
    def process_item(self, item, spider):
        """
        判断传入的item是否存在,可能再通过数据库操作的时候已经删除
        """
        if item:
            # 将item转换为es的数据
            item.save_to_es()

            return item
        else:
            print('item不存在')
            pass
