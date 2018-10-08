#!/usr/bin/python
# -*-coding:utf8-*-

import os
from Common.log import *


def listdir(path, list_name):
    list_name = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            listdir(file_path, list_name)
        elif os.path.splitext(file_path)[1] == '.zip':
            list_name.append(file_path)
        elif os.path.splitext(file_path)[1] == '.json':
            list_name.append(file_path)
        elif os.path.splitext(file_path)[1] == '.txt':
            list_name.append(file_path)

    return list_name


def del_zip():
    """
    删除压缩文件
    :return:
    """
    try:
        path = os.getcwd() + '/Files'
        list_name = []
        list_name = listdir(path, list_name)
        for filename in list_name:
            if os.path.exists(filename):
                os.remove(filename)
                logger.info('成功删除解压缩文件:%s' % filename)
                print('成功删除压缩文件:%s' % filename)
            else:
                logger.info('目标文件夹为空,文件不存在!')
                print('文件不存在')
    except Exception as e:
        logger.info(e)


def del_unzip():
    """
    删除解压缩文件
    :return:
    """
    try:
        path = os.getcwd() + '/files_unzip'
        list_name = []
        list_name = listdir(path, list_name)
        for filename in list_name:
            if os.path.exists(filename):
                os.remove(filename)
                logger.info('成功删除解压缩文件:%s' % filename)
                print('成功删除解压缩文件:%s' % filename)
            else:
                logger.info('目标文件夹为空,文件不存在!')
                print('文件不存在')
    except Exception as e:
        logger.info(e)



