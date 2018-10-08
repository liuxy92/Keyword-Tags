# encoding: utf-8

import flask
import os
import sys
import uuid

from flask import request, send_from_directory
from flask_script import Manager
from db_save import save
from Common.log import *

interface_path = os.path.dirname(__file__)
sys.path.insert(0, interface_path)  # 将当前文件的父目录加入临时系统变量


application = flask.Flask(__name__)
manager = Manager(application)


# post方法：上传文件的
@application.route('/upload', methods=['post'])
def upload():
    data = request.files
    dic = data.to_dict()
    logger.info('获取上传文件信息:{}'.format(dic))
    if 'file' not in request.files:
        logger.info('{"msg":"POST请求,携带的参数不是 file "}')
        return '{"msg":"POST请求,携带的参数不是 file "}'
    else:
        fname = request.files.get('file')  # 获取上传的文件
        if fname:
            zip_id = str(uuid.uuid1())
            fname.save(os.getcwd() + '/Files/' + zip_id + '-' + fname.filename)  # 保存文件到指定路径
            # 判断文件格式
            if fname.filename.split('.')[-1] == 'zip' or fname.filename.split('.')[-1] == 'json' or fname.filename.split('.')[-1] == 'txt':
                try:
                    save()
                    return '{"code":"200", "msg":"数据传送成功!"}'
                except EOFError as e:
                    logger.error(e)
                    return '{"msg":"json数据格式不正确!"}'
            else:
                logger.info('{"msg":"文件格式不正确,上传文件应为zip压缩文件"}')
                return '{"msg":"文件格式不正确,上传文件应为zip压缩文件"}'
        else:
            logger.info('{"msg":"获取上传对象为空!"}')
            return '{"msg":"获取上传对象为空!"}'


@application.route('/upload', methods=['GET'])
def accept():
    return '{"msg":"接口可以调用!"}'


if __name__ == '__main__':
    # application.run(port=8001, host='172.18.104.228', debug=True)
    manager.run()
