# -*-coding:utf8-*-

import zipfile
import os

from Common.log import *


def unzip():
    """
    文件解压
    :return:
    """
    file_list = os.listdir(r'./Files')
    for file_name in file_list:
        basepath = os.getcwd() + '/Files/'
        if os.path.splitext(basepath + file_name)[1] == '.zip':
            file_zip = zipfile.ZipFile(basepath + file_name, 'a')
            # 解压
            file_zip.extractall('./files_unzip')
            # 返回所有文件夹和文件
            file_names = file_zip.namelist()
            print(file_zip.namelist())
            # 返回该zip的文件名
            print(file_zip.filename)

            file_zip.close()
            # os.remove(basepath + file_name)

            return file_names
        else:
            pass
