# encoding: utf-8

import requests
import os
import threading
import json


# 上传文件到服务器
def web_requests():
    url = 'http://172.18.113.108:8001/upload'
    file = {
        'file': open(os.getcwd()+'/Base_files/msg.zip','rb'),
            }
    # headers = {
    #     'Content-Type': 'application/json'
    # }
    r = requests.post(url=url, files=file)
    print(r.status_code)
    #
    return r.text


# if __name__ == '__main__':
#     try:
#         i = 0
#         tasks = []          # 任务列表
#         task_number = 10
#         while i < task_number:
#             t = threading.Thread(target=web_requests)
#             tasks.append(t)  # 加入线程池，按需使用
#             t.start()   # 多线程并发
#     except Exception as e:
#         print(e)

if __name__ == '__main__':
    web_requests()
