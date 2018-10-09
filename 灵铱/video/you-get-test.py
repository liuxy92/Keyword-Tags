import os
import requests
from lxml import html
from pprint import pprint
import subprocess
import re
import json
# 可以查看那些视频网站可以下载视频https://github.com/soimort/you-get/pulls?page=1&q=is%3Apr+is%3Aopen
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
    'Referer': 'http://www.baidu.com'

}

# info = os.system(r'you-get https://stallman.org/rms.jpg')
info1 = ''.join(os.system(r'you-get --json http://video.baomihua.com/v/37768237?reportto=REC_37768237'))
print(type(info1))

# info = os.system(r'you-get https://my.tv.sohu.com/pl/9462669/102359552.shtml')
# url = os.system(r'you-get -u http://my.tv.sohu.com/pl/9449304/102093064.shtml')  # 获取真实的解析地址
# allurl = subprocess.getstatusoutput('you-get -u http://v.youku.com/v_show/id_XMzYzNDUwNDI4OA==.html')
# allurl = subprocess.getstatusoutput('you-get -u http://video.baomihua.com/v/37768237?reportto=REC_37768237')
# allurlqq = subprocess.getstatusoutput('you-get --url http://video.baomihua.com/v/37768237?reportto=REC_37768237')
# allurljson = subprocess.getstatusoutput('you-get --json http://video.baomihua.com/v/37768237?reportto=REC_37768237')
# print(allurl)
# print(allurljson)
# result = json.loads(allurljson[1])
# print(result['streams']['__default__']['src'][0])


# allurl = subprocess.getstatusoutput('you-get -u http://video.baomihua.com/v/37768330')
# print(allurlqq)
# print('*****************************')
# pattern = re.compile(r'URLs:(.*)')
# result = pattern.search(allurl)
# result = re.findall(r'URLs:(.*)', str(allurlqq))
# print(result[0][2:-2])
# print(allurlqq)
# print(allurljson)
# 测试可以提取出链接的网站：
# 优酷 搜狐  爆米花

# 使用 --url/-u 获得页面所有可下载URL列表. 使用 --json以获得JSON格式.

