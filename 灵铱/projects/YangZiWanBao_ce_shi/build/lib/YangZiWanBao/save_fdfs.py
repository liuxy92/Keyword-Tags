# -*- coding: utf-8 -*-
import os
import os
path = '/home/action/桌面/image/full'
from fdfs_client.client import *

client = Fdfs_client('/etc/fdfs/client.conf')

# ret = client.upload_by_filename('/home/action/桌面/image/full/e2116c6014dffa3746af0ec8496c2c1f2d010617.jpg')
# ret = client.upload_by_filename('/home/action/桌面/image/full//home/action/桌面/image/full/http://app.yzinter.com/d/file/news/livelihood/2017-10-24/a0af2713c15dc7be86ac1b9001308ce2.jpg')
#
# print(ret['Remote file_id'])
# print(type(ret['Remote file_id']))
#
# bs = str(ret['Remote file_id'], encoding = "utf8")
# print(bs)
# print(type(bs))
# b = []
# class Load_fdfs(object):

# def texttextrw():
#     ls = os.listdir(path)
#     for i in ls:
#         full_path = os.path.join(path, i)
#         b.append(full_path)
#         # print(full_path)
#         # print(type(full_path))
#         return full_path
    # ret = client.upload_by_filename('/home/action/桌面/image/full/' + zhao)
    # new_image_url = ret['Remote file_id']
    # # print('========================================')
    # bs = str(new_image_url, encoding="utf8")
    # return bs
def fullpath():
    ls = os.listdir(path)
    for i in ls:
        full_path = os.path.join(path, i)
        return full_path
