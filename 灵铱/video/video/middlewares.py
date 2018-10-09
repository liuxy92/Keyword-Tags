# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from fake_useragent import UserAgent
from redis import StrictRedis


class RandomUserAgentMiddlware(object):
    def process_request(self, request, spider):
        ua = UserAgent()
        request.headers['User-Agent'] = ua.random


class RandomProxyMiddleware(object):
    #动态设置ip代理
    def process_request(self, request, spider):
        redis = StrictRedis(host='116.196.69.103', port=6379, db=0, password=None)
        pro = redis.hmget('adsl', ['adsl1'])[0]
        a = pro.decode('utf-8')
        print(a)

        request.meta["proxy"] = "http://" + a
        # request.meta["proxy"] = "http://121.231.181.138:5073"