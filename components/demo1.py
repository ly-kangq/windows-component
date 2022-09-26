# flask
# html
# css bootstrap
# js
# jquery ajax

import numpy as np
import json
import suanpan
from suanpan.app import app
from suanpan.app.arguments import Json, Float, Npy
from suanpan.log import logger
from suanpan import g
from suanpan.utils import json
from suanpan.storage import storage
from flask import Flask, request, render_template, redirect, url_for, jsonify
import os
import math
import time
import datetime


def saveParams(params):
    # 将输入参数保存到 oss
    paramsFileKey = storage.getKeyInNodeConfigsStore("saved.json")
    paramsFilePath = storage.getPathInNodeConfigsStore("saved.json")
    json.dump(params, paramsFilePath)
    storage.upload(paramsFileKey, paramsFilePath)


def loadParams():
    # 从 oss 中读取参数
    paramsFileKey = storage.getKeyInNodeConfigsStore("saved.json")
    paramsFilePath = storage.getPathInNodeConfigsStore("saved.json")
    storage.download(paramsFileKey, paramsFilePath)
    return json.load(paramsFilePath)


def create_app():
    # create and configure the web
    web = Flask(__name__)

    @web.route('/')
    def to_home():
        if 'param1' in g.someParameter.keys():
            # 非首次启动页面
            logger.info('非首次启动页面')
            logger.info(f'g.someParameter = {g.someParameter}')
            # 将相关参数渲染到demo1.html页面中
            return render_template('demo1.html',param1=g.someParameter['param1'], param2=g.someParameter['param2'], 
            switchMode1=g.someParameter['switchMode1'],param_x1=g.someParameter['param_x1'],param_x2=g.someParameter['param_x2'],switchMode2=g.someParameter['switchMode2'])
        else:
            # 首次启动页面
            logger.info('首次启动页面')
            return render_template('demo1.html')             

    @web.route('/paramconfig',methods = ['POST', 'GET'])
    def to_paramconfig():
        if request.method == 'POST':
            # 当前端请求为POST时，接收发送过来的参数，并解析
            g.param1 = float(request.form['param1'])
            g.param2 = float(request.form['param2'])
            g.switchMode1 = request.form['switchMode1']
            # 由于可能存在param_x1或param_x2为空的情况，所以需要做条件判断，以免报错
            g.param_x1 = float(request.form['param_x1']) if request.form['param_x1'] != '' else request.form['param_x1']
            g.param_x2 = float(request.form['param_x2']) if request.form['param_x2'] != '' else request.form['param_x2']
            g.switchMode2 = request.form['switchMode2']

            # 打印接收到的参数
            logger.info(f'接收到以下参数：')
            logger.info(f'param1 = {g.param1}')
            logger.info(f'param2 = {g.param2}')
            logger.info(f'switchMode1 = {g.switchMode1}')
            logger.info(f'param_x1 = {g.param_x1}')
            logger.info(f'param_x2 = {g.param_x2}')
            logger.info(f'switchMode2 = {g.switchMode2}')
            
            # 将处理完之后的参数存入g.someParameter中，在下次打开页面时读取
            g.someParameter['param1'] = g.param1
            g.someParameter['param2'] = g.param2
            g.someParameter['switchMode1'] = g.switchMode1
            g.someParameter['param_x1'] = g.param_x1
            g.someParameter['param_x2'] = g.param_x2
            g.someParameter['switchMode2'] = g.switchMode2
            saveParams(g.someParameter)

            # 前端此时不需要拿到后端的数据，返回一个空对象即可
            return jsonify({})

    return web


def runFlask():
    # 初始化一个 flask
    web = create_app()
    # flask 由 suanpan app 加载
    app._stream.sioLoop.setWebApp(web)


def send_data(get_data, module_name):
    """
    规范向下游传递的数据格式
    :param get_data: 待传递的数据
    :param module_name: 当前组件的名称
    :return: 向下游传递的数据
    """
    app_id = os.environ.get("SP_APP_ID")
    node_id = os.environ.get("SP_NODE_ID")
    get_data["module_id"] = "/"+ app_id + "/" + node_id + "/" + "out1"
    get_data["timestamp"] = str(datetime.datetime.now())[:-3]
    get_data["module_name"] = module_name   

    # 若需传递每个位点的timestamp, type, unit,可按需增加
    # for idx in range(len(get_data["values"])):
    #     get_data["values"][idx]["timestamp"] = str(datetime.datetime.now())[:-3]
    #     get_data["values"][idx]["type"] = type(get_data["values"][idx]["value"]).__name__
    #     if "unit" not in get_data["values"][idx].keys():
    #         get_data["values"][idx]["unit"] = ""
    
    return get_data


# 本模板的功能是计算从弹窗返回的param1和param1之和
@app.afterInit
def afterInit(context):
    # 初始化相关变量
    g.Result = {}
    g.param1 = None
    g.param2 = None
    try:
        # 组件初始化，从oss读取保存的参数配置
        g.someParameter = loadParams()  # 创建一个g.someParameter变量，为{}
        logger.info(f'成功读取g.someParameter = {g.someParameter}')
        logger.info('参数从oss读取成功！')
        if 'param1' in g.someParameter.keys():
            g.param1 = g.someParameter['param1']
            g.param2 = g.someParameter['param2']
            g.switchMode1 = g.someParameter['switchMode1']
            g.param_x1 = g.someParameter['param_x1']
            g.param_x2 = g.someParameter['param_x2']
            g.switchMode2 = g.someParameter['switchMode2']
    except:
        pass

    # 在sdk中运行flask，会自动分配端口
    runFlask()


@app.input(Json(key="in1", alias="inputdata"))
@app.output(Json(key="out1", alias="result"))
def main(context):
    args = context.args
    inputData = args.inputdata
   
    if inputData is not None:
        if g.param1 and g.param2 is not None:
            g.Result['values']= g.param1+g.param2
            send_data(g.Result,'demo1')
            app.send({"result": g.Result})  # 发送结果
            logger.info(f'计算结果发送成功，结果为{g.Result}')
        else:
            logger.info('等待接收param1和param2')
       

if __name__ == "__main__":
    suanpan.run(app)