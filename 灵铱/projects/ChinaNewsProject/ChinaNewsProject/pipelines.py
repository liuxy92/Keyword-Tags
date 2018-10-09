# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import redis
import pymysql.cursors
import base64,json
from twisted.enterprise import adbapi

# 数据库连接池
from DBUtils.PooledDB import PooledDB
import io
import sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class ChinanewsprojectPipeline(object):
    def __init__(self):
        print('连接redis')
        self.red = redis.Redis(host="172.18.113.100", port=6379, db=2, decode_responses=True)
        print('连接成功')

        # 通过数据库链接池操作数据库
        print('连接数据库')
        db_config = {"host":'172.18.115.15', "port":3306, "user":'Dev3', "passwd":'123456', "db":'Im', "charset":'utf8'}
        print('链接数据库成功')
        self.pool = PooledDB(pymysql, 5, **db_config)
        # 5为连接池里的最少连接数

        self.conn = self.pool.connection()
        # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        # 存储redis
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
                # print(NewsTitle)
                # 判断爬取的title是否在redis key值为NewsTitle里在提示已存在，不在执行添加
                if NewsTitles not in value:
                    print(NewsTitles)
                    print(value)
                    if item['NewsTitle'] == '' or item['NewsContent'] == '':
                        print('数据为空')
                        pass
                    else:
                        print('不为空')
                        self.red.lpush('NewsTitle', base64.b64encode(item['NewsTitle'].encode('utf-8')))
                        # self.red.lpush('NewsTitle', (item['NewsTitle']))
                        items = json.dumps(dict(item))
                        self.red.lpush('201805news' + item['NewsCategory'], items)
                else:
                    print('redis数据已存在')
            else:
                print('出错')
        except:
            print('错误操作')

        # 数据库去重
        self.cursor.execute("SELECT NewsTitle FROM tbl_NewsDetails201805 WHERE NewsTitle='%s'" % item['NewsTitle'])
        cam_rows = self.cursor.fetchone()
        if cam_rows is not None:
            print(item['NewsTitle'])
            print('数据已存在')
            print('=========================')
            pass

        # 数据库插入新行数据
        else:
            # 删除内容和标题为空的数据
            if item['NewsTitle'] == '' or item['NewsContent'] == '':
                del item['NewsID']
            else:
                sql1 = 'insert into tbl_NewsDetails201805(NewsID,NewsCategory,SourceCategory,NewsType,NewsTitle,NewsContent,NewsRawUrl,SourceName,AuthorName,InsertDate,NewsDate,NewsClickLike,NewsBad,NewsRead,NewsOffline) ' \
                       'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                sql2 = 'insert into tbl_NewsFileManager(FileID, FileType, FileDirectory, FileDirectoryCompress, FileDate, FileLength, FileUserID, Description, NewsID,image_url)' \
                       'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                try:
                    # # 删除内容和标题为空的数据
                    # if item['NewsTitle'] == '' or item['NewsContent'] == '':
                    #     self.cursor.execute('DELETE FROM tbl_NewsDetails WHERE NewsID=%s' % item["NewsID"])

                    # 执行sql语句
                    self.cursor.execute(sql1, (
                        item['NewsID'], item['NewsCategory'], item['SourceCategory'], item['NewsType'], item['NewsTitle'],
                        item['NewsContent'], item['NewsRawUrl'], item['SourceName'], item['AuthorName'], item['InsertDate'],
                        item['NewsDate'], item['NewsClickLike'], item['NewsBad'], item['NewsRead'], item['NewsOffline']))

                    for dic in item['FileList']:
                        self.cursor.execute(sql2, (
                            dic['FileID'], dic["FileType"], dic["FileDirectory"], dic["FileDirectoryCompress"],
                            dic["FileDate"],
                            dic["FileLength"], dic["FileUserID"], dic["Description"], dic["NewsID"], dic["image_url"]
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
        self.cursor.close()
