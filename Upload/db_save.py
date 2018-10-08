# -*-coding:utf8-*-

import os
import json
import uuid
import time

import pymysql as mdb
from del_files import listdir, del_zip, del_unzip
from Common.log import *
from file_unzip import unzip
# from es_type import UserInfoType


def save():
    """
    数据提取保存es和数据库
    :return:
    """
    # file_names = UnzipDB.unzip()
    Dict = []
    basepath1 = os.getcwd() + '/files_unzip/'
    basepath2 = os.getcwd() + '/Files/'
    file_list = os.listdir(r'./Files')
    for filename in file_list:
        # 上传文件为zip压缩文件
        if filename.split('.')[-1] == 'zip':
            file_names = unzip()
            for file in file_names:
                with open(basepath1 + file) as f:
                    data = json.load(f)  # json.load()将数据转换为Python能够处理的格式并存储在data中
                    for dic in data:
                        dic['DataID'] = str(uuid.uuid1())
                        Dict.append(dic)

        # 上传文件为json后缀文件
        elif filename.split('.')[-1] == 'json' or filename.split('.')[-1] == 'txt':
            with open(basepath2 + filename) as f:
                data = json.load(f)  # json.load()将数据转换为Python能够处理的格式并存储在data中
                for dic in data:
                    dic['DataID'] = str(uuid.uuid1())
                    Dict.append(dic)
    logger.info('上传文件数据解析完毕!!!')


    """
    链接elasticsearch
    """
    from elasticsearch import Elasticsearch
    from elasticsearch import helpers

    start_time = time.time()    # 开始时间
    es = Elasticsearch(['172.18.113.113:9200'])
    try:
        i = 0
        actions = []
        for dict0 in Dict:
            action = {
                "_index": "im_usermsg",
                "_type": "tbl_NewsUserInfo",
                "_id": i,
                "_source": {
                    "DataID": dict0['DataID'],
                    "UserID": dict0['UserID'],
                    "NewsID": dict0['NewsID'],
                    "Accesslike": dict0['Accesslike'],
                    "AccessTime": dict0['AccessTime'],
                    "AccessNum": dict0['AccessNum'],
                    "ResidenceTime": dict0['ResidenceTime'],
                    "CommentsNum": dict0['CommentsNum'],
                    "AccessWay": dict0['AccessWay'],
                }
            }
            i += 1
            actions.append(action)
            if len(action) == 1000:
                helpers.bulk(es, actions)
                del actions[0:len(action)]
        if i > 0:
            helpers.bulk(es, actions)

        end_time = time.time()  # 结束时间
        t = end_time - start_time

        logger.info('json数据存储es成功! 本次共写入{}条数据,用时{}s'.format(i, t))
        print('本次共写入{}条数据,用时{}s'.format(i, t))
        print('json数据存储es成功!')
    except Exception as e:
        logger.error(e)
        print('json数据存储es失败!')

    """
    连接数据库
    """
    conn = mdb.connect(host='172.18.115.15', port=3306, user='Dev3', passwd='123456', db='Im', charset='utf8')
    logger.info('链接数据库成功!')
    # 如果使用事务引擎，可以设置自动提交事务，或者在每次操作完成后手动提交事务conn.commit()
    # conn.autocommit(1)  # conn.autocommit(True)
    # 使用cursor()方法获取操作游标
    cursor = conn.cursor()
    # 因该模块底层其实是调用CAPI的，所以，需要先得到当前指向数据库的指针

    # 插入数据
    sql = 'INSERT INTO tbl_NewsUserInfo(DataID,UserID,NewsID,Accesslike,AccessTime,AccessNum,ResidenceTime,CommentsNum,AccessWay)' \
          ' values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    try:
        for dict in Dict:
            cursor.execute(sql, (
                dict['DataID'], dict['UserID'], dict['NewsID'], dict['Accesslike'], dict['AccessTime'],
                dict['AccessNum'],
                dict['ResidenceTime'], dict['CommentsNum'], dict['AccessWay']
            ))
        conn.commit()
        logger.info('json数据成功入库!!!')
        print('json数据成功入库!!!')

    except Exception as e:
        logger.error(e)
        print('json数据入库失败!!!')

    cursor.close()  # 关闭链接
    conn.close()    #关闭游标

    # 删除下载路径下的压缩文件
    del_zip()
    # 删除解压路径下的解压文件
    del_unzip()

    print('程序执行完毕!!!')
