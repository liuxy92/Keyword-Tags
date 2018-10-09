# -*- coding: utf-8 -*-

import requests
from lxml import etree
import re
from hashlib import md5
import os
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
    'Referer': 'http://www.baidu.com'

}

# url = 'https://475-5.vod.tv.itc.cn/sohu/v1/TmwmoAIOfJWHg4xvNt8duKADPA0Mo28mDAdLb2CWPFXUyYbSoO2VqVw.mp4?k=n2qJzZ&p=j9lvzSw3oSsmomk7op17op1UqprComvAhRYCzSwWjWlvzSxiqmXGoLrWXWPIWho70ScAZMoUoTWCr&r=TUOgXpxnyLbUZDWS0pviyF2Xvm9Auh2DT8se8EAAeVcNZT6e0AoAfSyUNBA3gpEmeJbLftfOzYoCNLfcWFy4vmXAyBj&q=OpCGoKOyzSwdhWwIWDWSotE7ZD6OWOXsRYXsRhNHfFyS0F2OfDb4fOyXWBoURD6OfhoUZDJ&cip=133.18.196.47&ua=&ch=tv&catcode=122102&prod=flash&pt=1&plat=flash_Linux&n=10&a=53&cip=133.18.196.47&vid=4777120&tvid=101993986&uid=15163358088086404392&sz=1850_448&md=fUg3ykOpVBdKjM8nFee+MLdx0vu6vINFxMxjIg==225&uuid=a5e8f1e5-c155-e777-ef6e-71e4d970b8bb&url=https%3A//tv.sohu.com/20180517/n600520064.shtml'

# url = 'https://475-5.vod.tv.itc.cn/sohu/v1/TmwmoAIOfJWHg4xvNt8duKADPA0Mo28mDAdLb2CWPFXUyYbSoO2VqVw.mp4?k=n2qJzZ&p=j9lvzSw3oSsmomk7op17op1UqprComvAhRYCzSwWjWlvzSxiqmXGoLrWXWPIWho70ScAZMoUoTWCr&r=TUOgXpxnyLbUZDWS0pviyF2Xvm9Auh2DT8se8EAAeVcNZT6e0AoAfSyUNBA3gpEmeJbLftfOzYoCNLfcWFy4vmXAyBj&q=OpCGoKOyzSwdhWwIWDWSotE7ZD6OWOXsRYXsRhNHfFyS0F2OfDb4fOyXWBoURD6OfhoUZDJ&cip=133.18.196.47&ua=&ch=tv&catcode=122102&prod=flash&pt=1&plat=flash_Linux&n=10&a=53&cip=133.18.196.47&vid=4777120&tvid=101993986&uid=15163358088086404392&sz=1850_448&md=fUg3ykOpVBdKjM8nFee+MLdx0vu6vINFxMxjIg==225&uuid=a5e8f1e5-c155-e777-ef6e-71e4d970b8bb&url=https%3A//tv.sohu.com/20180517/n600520064.shtml'
# url = 'http://video.yidianzixun.com/video/get-url?key=user_upload/1527208480260d2d31cbedac78cb1e879cbec038d7455.mp4'
# url = 'http://upos-hz-mirrorkodo.acgvideo.com/upgcxcode/83/17/39911783/39911783-1-80.flv?e=ig8euxZM2rNcNbug7wNVhoM17wK37wdVNEVEuCIv29hEn0lqXg8Y2ENvNCImNEVEUJ1miI7MT96fqj3E9r1qNCNEto8g2ENvN03eN0B5tZlqNxTEto8BTrNvNeZVuJ10Kj_g2UB02J0mN0B599M=&deadline=1527582525&dynamic=1&gen=playurl&oi=1928474620&os=kodo&platform=pc&rate=724200&trid=82fc23f90fb746908816a4cc23671e2d&uipk=5&uipv=5&um_deadline=1527582525&um_sign=f290e0bad3446f012e5ff2741e1dd40b&upsig=a570378bff82d0a4af1744b5f5262237'
# url = 'http://123.126.115.4/sohu/v1/Tm1ATmwioEIXfMPBhFdN0AeIvguxkkBXSl7aRvmaEBgXpxWsm3UtUw.mp4?k=MdVh1Y&p=j9lvzSw3oLXUqpv3qLoG0SPWXZxIWhoVqTPcWh1OfOeXWDeOwmvGZD6S0pviNF2mqLKBgr&r=TmI20LscWOo70Sc2ZDASqt8IS3u4WOGqa5ecaIDzEEeWDyMySXRqAdNqM9UeEAdN6k6TYoCNLfcWGbtwmXAyBj&q=OpCGhW7IWJodRDbsfYvSotE7ZD6sWFXOfFvHfFyHfJeOwmbcWJe4fG1XZYNSqD2sWhNSqF2sY&cip=114.242.47.252'
# url = 'http://vali.cp31.ott.cibntv.net/6773430E6BD317136D1175ED9/03000C01005B0E147695F1B3A806D8E06C8B03-0DA4-4E26-8B18-FA9E88119C25.mp4?ccode=0510&duration=166&expire=18000&psid=924dabfd59b2913704fb0ccfd9d9228e&sp=&ups_client_netip=72f22ffc&ups_ts=1527726529&ups_userid=&utid=vi%2BWEwuH1w8CAXLyL%2FxGsVOY&vid=XMzYzNDUwNDI4OA%3D%3D&vkey=B7253fcea4dbf602e6f401fc681491c4d&s=efbfbd17efbfbdefbfbd'

url = 'http://video.yidianzixun.com/video/get-url?key=user_upload/1528253189350a20cfe5466f509467910726a4f46a0ad.mp4'
response = requests.get(url, headers=headers).content

file_name = md5(response).hexdigest()
file = '{0}/{1}.{2}'.format(os.getcwd(), file_name, 'mp4')
full_name = os.getcwd() + "/" + file_name + '.mp4'
if not os.path.exists(file):
    with open(file, "wb") as f:
        f.write(response)
