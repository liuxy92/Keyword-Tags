# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import redis
import pymysql.cursors
from twisted.enterprise import adbapi

# 数据库连接池
from DBUtils.PooledDB import PooledDB
import io
import sys
import base64
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class V1ProjectPipeline(object):
    def __init__(self):
        print('连接redis')
        self.red = redis.Redis(host="172.18.113.100", port=6379, db=2, decode_responses=True)
        print('连接成功')
        print('连接mysql服务器')
        db_config = {"host": '172.18.115.15', "port": 3306, "user": 'Dev3', "passwd": '123456', "db": 'Im',
                     "charset": 'utf8'}
        self.pool = PooledDB(pymysql, 5, **db_config)
        # 5为连接池里的最少连接数
        self.conn = self.pool.connection()
        # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            #获取redis所有为NewsTitle的key值
            keys = self.red.keys('NewsTitle')
            #转变类型为字符串
            key = ''.join(keys)
            #lrange获取所有key值为NewsTitle的内容
            value = self.red.lrange('%s'%key,'0','-1')
            #判断内容是否为空
            if len(value) >= 0:
                NewsTitless = base64.b64encode(item['NewsTitle'].encode('utf-8'))
                NewsTitles = str(NewsTitless,'utf-8')
                # print(NewsTitle)
                #判断爬取的title是否在redis key值为NewsTitle里在提示已存在，不在执行添加
                if NewsTitles not in value:
                    print(NewsTitles)
                    print(value)
                    if item['NewsTitle'] == '' or item['NewsContent'] == '':
                        print('数据为空')
                        pass
                    else:
                        print('不为空')
                        self.red.lpush('NewsTitle',base64.b64encode(item['NewsTitle'].encode('utf-8')))
                        self.red.lpush('201805news' + item['NewsCategory'], item)
                else:
                    print('redis数据已存在')
            else:
                print('出错')
        except:
            print('错误操作')
        # 数据库去重
        self.cur.execute("SELECT NewsTitle FROM tbl_NewsDetails201805 WHERE NewsTitle='%s'" % item['NewsTitle'])
        cam_rows = self.cur.fetchone()
        if cam_rows is not None:
            print(item['NewsTitle'])
            print('数据已存在')
            print('=========================')
            pass
        else:
            sql1 = 'insert ignore into tbl_NewsDetails201805(NewsID, NewsCategory, SourceCategory, NewsType, NewsTitle, NewsRawUrl, SourceName, AuthorName, InsertDate, NewsContent, NewsDate, NewsClickLike, NewsBad, NewsRead, NewsOffline)' \
                   'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            sql2 = 'insert into tbl_NewsFileManager(FileID, FileType, FileDirectory, FileDirectoryCompress, FileDate, FileLength, FileUserID, Description, NewsID,image_url)' \
                   'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
            try:
                if item['NewsTitle'] == '' or item['NewsContent'] == '':
                    self.cur.execute('DELETE FROM tbl_NewsDetails201805 WHERE NewsID=%s' % item["NewsID"])
                else:
                    self.cur.execute(sql1, (
                        item['NewsID'], item["NewsCategory"], item["SourceCategory"], item["NewsType"], item["NewsTitle"],
                        item["NewsRawUrl"], item["SourceName"], item["AuthorName"], item["InsertDate"], item["NewsContent"],
                        item['NewsDate'], item['NewsClickLike'], item['NewsBad'], item['NewsRead'], item['NewsOffline']
                    ))

                    self.cur.execute(sql2, (
                        item['FileID'], item["FileType"], item["FileDirectory"], item["FileDirectoryCompress"],
                        item["FileDate"],
                        item["FileLength"], item["FileUserID"], item["Description"], item["NewsID"], item["image_url"]
                    ))
                self.conn.commit()
            except Exception as e:
                print(e)
                print("执行sql语句失败")

            return item
    def close_conn(self, spider):
        # 关闭链接
        self.conn.close()
        # 关闭游标
        self.cur.close()

