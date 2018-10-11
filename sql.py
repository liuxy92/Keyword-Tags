#!/home/user/py35env/bin/python3

import pymysql
import datetime


def mysql():
    # db = pymysql.connect(host="10.100.105.133", user="Dev1", port="3306", passwd="Dev1", db="xuexi", charset="utf8")
    db = pymysql.connect(host='172.18.115.15', port=3306, user='Dev3', passwd='123456', db='Im', charset='utf8')
    cursor = db.cursor()
    # 根据当前月份创建新的学习模块表
    i = datetime.datetime.now()
    m = i.month
    if len(str(m)) == 1:
        b = "%s0%s" % (i.year, i.month)
    else:
        b = "%s%s" % (i.year, i.month)
    """
    创建学习模块信息表
    """
    sql1 = """CREATE TABLE `tbl_LRDetails{0}` (
      `LRID` varchar(50) NOT NULL,
      `LRCategory` varchar(36) DEFAULT NULL,
      `LRSourceCategory` varchar(36) DEFAULT NULL,
      `LRType` int(11) DEFAULT NULL,
      `LRTitle` varchar(200) DEFAULT NULL,
      `LRContent` longtext,
      `LRRawUrl` varchar(500) DEFAULT NULL,
      `LRDate` datetime NOT NULL,
      `LRClickLike` int(11) NOT NULL DEFAULT '0',
      `LRBad` int(11) NOT NULL DEFAULT '0',
      `LRRead` int(11) NOT NULL DEFAULT '0',
      `LRSourceName` varchar(200) DEFAULT NULL,
      `LRInsertDate` datetime DEFAULT NULL,
      `LROffline` int(10) NOT NULL DEFAULT '0' COMMENT '标记LR学习资料是否下线，默认0-上线；1-下线',
      `LRAuthor` varchar(200) DEFAULT NULL,
      PRIMARY KEY (`LRID`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;""".format(b)

    cursor.execute(sql1)
    print("CREATE TABLE1 OK")

    """
    创建学习模块下载文件表
    """
    sql2 = """CREATE TABLE `tbl_LRFileManager{0}` (
      `FileID` varchar(50) NOT NULL,
      `FileType` int(2) NOT NULL,
      `FileDirectory` varchar(200) NOT NULL,
      `FileDirectoryCompress` varchar(200) DEFAULT NULL,
      `FileDate` datetime NOT NULL,
      `LRID` varchar(50) DEFAULT NULL,
      PRIMARY KEY (`FileID`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;""".format(b)

    cursor.execute(sql2)
    print("CREATE TABLE2 OK")

    # 关闭数据库连接
    db.close()
    cursor.close()


if __name__ == '__main__':
    mysql()
