import os
import requests
from lxml import html
from pprint import pprint

def cmd_download(url, filename):

    info = os.system(r'you-get --debug -o C:\Users\rHotD\Downloads\wangyi_open\Linear_algebraic_exercises -O {} {}'.format(filename, url))

    print(info)

    return 1

# 课程首页 url
# 线性代数 url
response = requests.get('http://open.163.com/special/opencourse/daishu.html')

# 线性代数习题 url
response = requests.get('http://open.163.com/special/opencourse/mitxianxingdaishuxitike.html')

tree = html.fromstring(response.text)

url_list = tree.xpath('//div[@class="m-mn"]//table[2]//tr/td[1]/a//@href')
filename_list = tree.xpath('//div[@class="m-mn"]//table[2]//tr/td[1]/a/text()')
filename_list = list(map(lambda x:x.strip(), filename_list))
pprint(filename_list)

# url_list = ['http://open.163.com/movie/2010/11/7/3/M6V0BQC4M_M6V29E773.html', 'http://open.163.com/movie/2010/11/P/P/M6V0BQC4M_M6V29EGPP.html', 'http://open.163.com/movie/2010/11/H/O/M6V0BQC4M_M6V29FCHO.html', 'http://open.163.com/movie/2010/11/3/S/M6V0BQC4M_M6V29F33S.html', 'http://open.163.com/movie/2010/11/J/K/M6V0BQC4M_M6V29FRJK.html', 'http://open.163.com/movie/2010/11/B/5/M6V0BQC4M_M6V2AB1B5.html', 'http://open.163.com/movie/2010/11/H/H/M6V0BQC4M_M6V2ABAHH.html', 'http://open.163.com/movie/2010/11/V/8/M6V0BQC4M_M6V2ABHV8.html', 'http://open.163.com/movie/2010/11/C/T/M6V0BQC4M_M6V2ACDCT.html', 'http://open.163.com/movie/2010/11/D/T/M6V0BQC4M_M6V2ADFDT.html', 'http://open.163.com/movie/2010/11/2/T/M6V0BQC4M_M6V2AJS2T.html', 'http://open.163.com/movie/2010/11/T/E/M6V0BQC4M_M6V2AIUTE.html', 'http://open.163.com/movie/2010/11/9/K/M6V0BQC4M_M6V2AJ69K.html', 'http://open.163.com/movie/2010/11/M/H/M6V0BQC4M_M6V2AJEMH.html', 'http://open.163.com/movie/2010/11/J/U/M6V0BQC4M_M6V2AJLJU.html', 'http://open.163.com/movie/2010/11/P/U/M6V0BQC4M_M6V2AOJPU.html', 'http://open.163.com/movie/2010/11/L/S/M6V0BQC4M_M6V2AORLS.html', 'http://open.163.com/movie/2010/11/5/0/M6V0BQC4M_M6V2AP150.html', 'http://open.163.com/movie/2010/11/3/4/M6V0BQC4M_M6V2APP34.html', 'http://open.163.com/movie/2010/11/0/C/M6V0BQC4M_M6V2AQ40C.html', 'http://open.163.com/movie/2010/11/R/8/M6V0BQC4M_M6V2AV2R8.html', 'http://open.163.com/movie/2010/11/G/L/M6V0BQC4M_M6V2AV6GL.html', 'http://open.163.com/movie/2010/11/B/M/M6V0BQC4M_M6V2AVIBM.html', 'http://open.163.com/movie/2010/11/A/V/M6V0BQC4M_M6V2AVOAV.html', 'http://open.163.com/movie/2010/11/6/P/M6V0BQC4M_M7E4C9V6P.html', 'http://open.163.com/movie/2010/11/L/4/M6V0BQC4M_M6V2AVUL4.html', 'http://open.163.com/movie/2010/11/7/7/M6V0BQC4M_M6V2B4U77.html', 'http://open.163.com/movie/2010/11/3/P/M6V0BQC4M_M6V2B5J3P.html', 'http://open.163.com/movie/2010/11/K/E/M6V0BQC4M_M6V2B5OKE.html', 'http://open.163.com/movie/2010/11/1/G/M6V0BQC4M_M6V2B5R1G.html', 'http://open.163.com/movie/2010/11/P/J/M6V0BQC4M_M6V2B60PJ.html', 'http://open.163.com/movie/2010/11/4/Q/M6V0BQC4M_M6V2BA04Q.html', 'http://open.163.com/movie/2010/11/N/8/M6V0BQC4M_M6V2BA6N8.html', 'http://open.163.com/movie/2010/11/Q/9/M6V0BQC4M_M6V2BADQ9.html', 'http://open.163.com/movie/2010/11/1/H/M6V0BQC4M_M6V2BAN1H.html']

url_list = ['http://open.163.com/movie/2016/4/H/1/MBKJ0DQ52_MBKJ0MDH1.html', 'http://open.163.com/movie/2016/4/J/I/MBKJ0DQ52_MBKJ0KNJI.html', 'http://open.163.com/movie/2016/4/O/J/MBKJ0DQ52_MBKJ0M8OJ.html', 'http://open.163.com/movie/2016/4/5/B/MBKJ0DQ52_MBLPMC95B.html', 'http://open.163.com/movie/2016/4/V/0/MBKJ0DQ52_MBLPMH3V0.html', 'http://open.163.com/movie/2016/4/J/2/MBKJ0DQ52_MBLPMLRJ2.html', 'http://open.163.com/movie/2016/4/6/J/MBKJ0DQ52_MBMGQPS6J.html', 'http://open.163.com/movie/2016/4/V/1/MBKJ0DQ52_MBMGQU9V1.html', 'http://open.163.com/movie/2016/4/E/V/MBKJ0DQ52_MBMGR18EV.html', 'http://open.163.com/movie/2016/4/K/8/MBKJ0DQ52_MBN2TTTK8.html', 'http://open.163.com/movie/2016/4/3/9/MBKJ0DQ52_MBN2TUT39.html', 'http://open.163.com/movie/2016/4/4/H/MBKJ0DQ52_MBN2U324H.html', 'http://open.163.com/movie/2016/4/3/I/MBKJ0DQ52_MBNI7H33I.html', 'http://open.163.com/movie/2016/4/Q/B/MBKJ0DQ52_MBNI7N9QB.html', 'http://open.163.com/movie/2016/4/0/K/MBKJ0DQ52_MBNI82I0K.html', 'http://open.163.com/movie/2016/4/S/G/MBKJ0DQ52_MBO4BMVSG.html', 'http://open.163.com/movie/2016/4/S/U/MBKJ0DQ52_MBO4BS2SU.html', 'http://open.163.com/movie/2016/4/F/C/MBKJ0DQ52_MBO4C07FC.html', 'http://open.163.com/movie/2016/4/G/M/MBKJ0DQ52_MBOK1DGGM.html', 'http://open.163.com/movie/2016/4/6/F/MBKJ0DQ52_MBORHQ86F.html', 'http://open.163.com/movie/2016/4/5/G/MBKJ0DQ52_MBORHTS5G.html', 'http://open.163.com/movie/2016/4/1/V/MBKJ0DQ52_MBPD3UV1V.html', 'http://open.163.com/movie/2016/4/N/3/MBKJ0DQ52_MBPD42SN3.html', 'http://open.163.com/movie/2016/4/R/G/MBKJ0DQ52_MBPD47BRG.html', 'http://open.163.com/movie/2016/4/4/5/MBKJ0DQ52_MBPT38M45.html', 'http://open.163.com/movie/2016/4/3/U/MBKJ0DQ52_MBPT3II3U.html', 'http://open.163.com/movie/2016/4/T/9/MBKJ0DQ52_MBPT3IET9.html', 'http://open.163.com/movie/2016/4/0/L/MBKJ0DQ52_MBQF44O0L.html', 'http://open.163.com/movie/2016/4/G/V/MBKJ0DQ52_MBQF4FBGV.html', 'http://open.163.com/movie/2016/4/Q/2/MBKJ0DQ52_MBQF4M7Q2.html', 'http://open.163.com/movie/2016/4/D/4/MBKJ0DQ52_MBQUMH1D4.html', 'http://open.163.com/movie/2016/4/K/D/MBKJ0DQ52_MBQUMKUKD.html', 'http://open.163.com/movie/2016/4/E/K/MBKJ0DQ52_MBQUNJMEK.html', 'http://open.163.com/movie/2016/4/3/6/MBKJ0DQ52_MBQUQV336.html', 'http://open.163.com/movie/2016/4/F/E/MBKJ0DQ52_MBR0VPVFE.html', 'http://open.163.com/movie/2016/4/9/A/MBKJ0DQ52_MBR0VUD9A.html']
filename_list = ['线性代数中的几何学',
                 '核心思想概述',
                 '矩阵的消去法',
                 '逆矩阵',
                 'LU分解',
                 '三维空间的子空间',
                 '向量子空间',
                 '解Ax=0',
                 '解Ax=b',
                 '向量空间的基底与维数',
                 '四个基本子空间的计算',
                 '矩阵的空间',
                 '测验题目讲解1',
                 '图像与网络',
                 '正交向量和子空间',
                 '子空间上的投影',
                 '最小二乘逼近',
                 'Gram-Schmidt正交化',
                 '行列式的性质',
                 '行列式',
                 '行列式与体积',
                 '特征值和特征向量',
                 '矩阵的方幂',
                 '微分方程与exp(At)',
                 '马尔科夫矩阵',
                 '测验题目讲解2',
                 '对称矩阵与正定矩阵',
                 '复矩阵',
                 '正定矩阵与极小值',
                 '相似矩阵',
                 '奇异值分解的运算',
                 '线性变换',
                 '基的变换',
                 '广义逆',
                 '测验题目讲解3',
                 '期末考试题讲解']
for url,filename in zip(url_list[1:5], filename_list[1:5]):
    print(url, filename)
    status_code = cmd_download(url, filename)
    if status_code:
        pass