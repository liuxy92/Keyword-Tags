# -*- coding: utf-8 -*-

import requests
from lxml import etree
import re


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
    'Referer': 'http://www.baidu.com'

}

url = 'http://mil.huanqiu.com/milmovie/2018-05/12047487.html'
response = requests.get(url, headers=headers)
response.encoding='utf-8'
html = etree.HTML(response.text)
link = html.xpath("//div[@class='l_a']/h1/text()")
content = html.xpath("//div[@class='la_con']/p/text()")
print(link)
print(content)

