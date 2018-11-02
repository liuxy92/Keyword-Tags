# -*-coding:utf8-*-

import pymysql
import time,datetime
import uuid

# 链接数据库
conn = pymysql.connect(host='172.18.115.15', port=3306, user='Dev3', passwd='123456', db='Im', charset='utf8')
cursor = conn.cursor()
print('链接数据库成功')


def user():
    """
        获取用户id
    """
    user_list = []
    cursor.execute("SELECT userid FROM tbl_news_user")
    rows = cursor.fetchall()
    # print(list(rows))
    for row in list(rows):
        obj = row[0]
        user_list.append(obj)
    # print(user_list)

    return user_list


def news_tags():
    user_list = user()
    weight = 1
    for user_id in user_list:
        cursor.execute("SELECT * FROM tbl_NewsUserInfo WHERE (AccessTime between '2018-09-24' AND '2018-09-29')AND UserID='%s'" % user_id)
        cam_rows = cursor.fetchall()
        if cam_rows is ():
            pass
            # print('用户id:{}, 此用户暂无浏览新闻日志!!!'.format(user_id))
        else:
            # 将元组转换成列表
            ll = list(cam_rows)
            # 将用户浏览信息通过访问新闻页面时长正排序
            positive_ll = sorted(ll, key=lambda x: x[6])
            # 获取用户最喜欢的一条新闻
            new_list = positive_ll[-3:]
            for favorite in new_list:
                news_id = favorite[2]
                # print(news_id)

                # 根据新闻ID的实时年月，查询对应库表新闻详情数据
                b = news_id.split('-')[0]
                print(b)
                cursor.execute("SELECT * FROM tbl_NewsDetails{0} WHERE NewsID='%s'".format(b) % news_id)
                cam_rows1 = cursor.fetchall()
                news_ll = list(cam_rows1)
                # print(news_ll)
                # 新闻大标签
                news_category = news_ll[0][1]
                cursor.execute("SELECT CategoryName FROM tbl_NewsCategory WHERE CategoryCode='%s'" % news_category)
                cam_rows2 = cursor.fetchone()
                tag = cam_rows2[0]
                insertdate = time.strftime('%Y-%m-%d %H-%M-%S', time.localtime(time.time()))

                """
                新闻标签入库
                """
                # 数据库去重
                cursor.execute("SELECT TagID,TagWeight FROM tbl_NewsTags WHERE (NewsCategory='%s' AND UserID='%s')" % (news_category, user_id))
                row = cursor.fetchone()
                # print(row)

                # 更新用户信息
                if row is not None:
                    new_weight = row[1] + 1
                    sql1 = "UPDATE tbl_NewsTags SET TagWeight='%s' WHERE TagID='%s'" % (new_weight, row[0])
                    cursor.execute(sql1)
                    # 提交数据
                    conn.commit()
                    print('用户id:{} --- 数据更新成功!!'.format(user_id))

                # 插入新的用户信息
                else:
                    sql = 'INSERT INTO tbl_NewsTags(TagID,UserID,NewsCategory,NewsTag,InsertDate,TagWeight)' \
                          ' values(%s,%s,%s,%s,%s,%s)'
                    try:
                        tag_id = str(uuid.uuid1())
                        cursor.execute(sql, (
                            tag_id, user_id, news_category, tag, insertdate, weight
                        ))
                        conn.commit()
                        print('数据入库成功!')
                    except Exception as e:
                        print('数据入库失败! 失败原因:{}'.format(e))

    cursor.close()  # 关闭游标
    conn.close()   # 关闭连接


if __name__ == '__main__':
    news_tags()
    # user()

