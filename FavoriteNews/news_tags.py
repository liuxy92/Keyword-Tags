# -*-coding:utf8-*-

import pymysql
import os
import uuid
import time

from GetTageWord import *

# 链接数据库
conn = pymysql.connect(host='172.18.115.15', port=3306, user='Dev3', passwd='123456', db='Im', charset='utf8')
cursor = conn.cursor()
print('链接数据库成功')

l = ['a', 'b', 'c']

for user_id in l:
    cursor.execute("SELECT * FROM tbl_NewsUserInfo WHERE UserID='%s'" % user_id)
    cam_rows = cursor.fetchall()
    # 将元组转换成列表
    ll = list(cam_rows)
    # 将用户浏览信息通过访问新闻页面时长正排序
    positive_ll = sorted(ll, key=lambda x:x[6])
    # 获取最喜欢新闻
    new_list = positive_ll[-1:]
    # print(new_list)
    # sql = 'INSERT INTO tbl_NewsUserInfo(DataID,UserID,NewsID,Accesslike,AccessTime,AccessNum,ResidenceTime,CommentsNum,AccessWay)' \
    #       ' values(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    for favorite in new_list:
        news_id = favorite[2]
        # print(news_id)
        cursor.execute("SELECT * FROM tbl_NewsDetails WHERE NewsID='%s'" % news_id)
        cam_rows1 = cursor.fetchall()
        news_ll = list(cam_rows1)
        # 提取新闻标题关键字
        for a in news_ll:
            title = a[4]
            all_words_list = TextProcessing(title)
            # print(all_words_list)
            # 生成stopwords_set
            stopwords_file = os.getcwd() + '/stopwords_cn.txt'
            stopwords_set = MakeWordsSet(stopwords_file)

            feature_words = words_dict(all_words_list, 2, stopwords_set)
            # print(feature_words)

            # 关键字入库
            sql = 'INSERT INTO tbl_NewsFavorite(TagID,NewsID,KeyWords,InsertDate)' \
                  ' values(%s,%s,%s,%s)'
            try:
                kw = []
                for dic in feature_words:
                    a = []
                    weight = dic['weight']
                    word = dic['words']
                    a.append(word)
                    a.append(weight)
                    kw.append(tuple(a))
                keywords = ','.join(str(i) for i in kw)
                insertdate = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))
                tag_id = str(uuid.uuid1())
                # 执行sql语句
                cursor.execute(sql, (
                    tag_id, news_id, keywords, insertdate
                ))
                conn.commit()
                print('数据入库成功!')
            except Exception as e:
                print('数据入库失败原因:{}'.format(e))

cursor.close()  # 关闭链接
conn.close()  # 关闭游标


