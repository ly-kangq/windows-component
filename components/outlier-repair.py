import suanpan
from flask import Flask, request, render_template, redirect, url_for, jsonify
from suanpan import g
from suanpan.app import app
from suanpan.log import logger
from suanpan.utils import json
from suanpan.storage import storage
from suanpan.app.arguments import String, Json
import re
import numpy as np
from datetime import datetime
import os

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
        if len(g.someParameter.keys()) > 0:
            # 二次启动页面
            logger.info('connect web!!!')
            logger.info(f'g.someParameter = {g.someParameter}')
            return render_template('outlier-repair.html', 
            tolerance_error_rec=g.someParameter['tolerance_error_rec'])
        else:
            # 初始化页面
            logger.info('connect web!')
            return render_template('outlier-repair.html')             

    @web.route('/paramconfig',methods = ['POST', 'GET'])
    def to_paramconfig():
        if request.method == 'POST':

            g.tolerance_error_rec = request.form['tolerance_error']
            g.method = request.form['Method']
            g.tolerance_error = float(g.tolerance_error_rec)

            logger.info(f'接收到以下参数：')

            logger.info(f'tolerance_error = {g.tolerance_error}')
            logger.info(f'type tolerance_error = {type(g.tolerance_error)}')
            logger.info(f'method = {g.method}')
            logger.info(f'type method = {type(g.method)}')

            g.someParameter['tolerance_error'] = g.tolerance_error
            g.someParameter['method'] = g.method
            g.someParameter['tolerance_error_rec'] = g.tolerance_error_rec
            data = g.someParameter
            saveParams(data)
            return jsonify(data)

    return web


def runFlask():
    # 初始化一个 flask
    web = create_app()
    # flask 由 suanpan app 加载
    app._stream.sioLoop.setWebApp(web)


def parseInput(para):
    for i in range(len(para)):
        para[i] = float(para[i])
    return para


def control_precision(param):
    pattern = re.compile(r'.*?\d+(\.)(\d){6}')
    if isinstance(param, list):
        for indx, item in enumerate(param):
            item = "{:.7f}".format(item)
            if item != str(float("inf")) and item != str(-float('inf')):
                try:
                    param[indx] = float(re.match(pattern, item).group())
                except(AttributeError):
                    param[indx] = np.nan
            else:
                pass
    elif isinstance(param, int) or isinstance(param, float):
        param = "{:.7f}".format(param)
        if param != str(float("inf")) and param != str(-float('inf')):
            param = float(re.match(pattern, param).group())
        else:
            pass
    else:
        logger.info(f"Parameter: {param}  {type(param)}")
        logger.error(f"Parameter is illegal")
    return param


def bound_check(original_optimization_variable, variables):
    bound_check_vars = []
    bound_check_names = []
    
    for var in variables:
        temp_check_vars = []
        temp_check_vars.append(var["value"])
        for points in original_optimization_variable["values"]:
            if points["name"] == var["name"] + "_lb":
                temp_check_vars.append(points["value"])
        for points in original_optimization_variable["values"]:
            if points["name"] == var["name"] + "_ub":
                temp_check_vars.append(points["value"])
        if len(temp_check_vars) == 3:
            bound_check_vars.append(temp_check_vars)
            bound_check_names.append(var["name"])

    wrong_vars = []
    logger.info("\n")
    logger.info(f"check vars name: {bound_check_names}")
    logger.info(f"check vars: {bound_check_vars}")
    for idx, check_lst in enumerate(bound_check_vars):
        if check_lst[0] < check_lst[1] or check_lst[0] > check_lst[2]:
            wrong_vars.append(bound_check_names[idx])
    return wrong_vars


def str_judge(value):
    """判断value是否为str类型，是否为空值"""
    if isinstance(value,str):
        if len(value) != 0:
            value = float(value)
        else:
            value = np.nan
    return value


def ResetGlobalVariables():
    g.Var_Set = list()
    g.Var_Ub = []
    g.Var_Lb = []
    g.Var_Init = []
    g.Var_Other = []
    g.Send_Vars = {}


@app.afterInit
def afterInit(context):
    
    ResetGlobalVariables()

    try:
        # 组件初始化，从oss读取保存的参数配置
        g.someParameter = loadParams()
        logger.info(f'成功读取g.someParameter = {g.someParameter}')
        logger.info('参数从oss读取成功！')
        if len(g.someParameter.keys()) > 0:
            g.tolerance_error = g.someParameter['tolerance_error']
            g.method = g.someParameter['method']
    except:
        pass

    # 在sdk中运行flask，会自动分配端口
    runFlask()



@app.input(Json(key="in1", alias="original_optimization_variable"))
@app.output(Json(key="out1", alias="checked_optimization_variable"))
def main(context):
    args = context.args
    original_optimization_variable = args.original_optimization_variable

    if len(g.someParameter) != 0:
        if original_optimization_variable is not None:
            logger.info(f"original_optimization_variable:{original_optimization_variable}")

            g.Send_Vars = original_optimization_variable
            g.Variables = list()
            logger.info(f"len: {len(original_optimization_variable['values'])}")
            for variable in original_optimization_variable["values"]:
                if all(value not in variable["name"] for value in ["_lb","_ub"]):
                    g.Variables.append(variable)


            logger.info(f"vars: {g.Variables}")

            wrong_vars = bound_check(original_optimization_variable, g.Variables)
            if len(wrong_vars) != 0:
                logger.info(f"Original point is out of range!")
                logger.info(f"The points: {wrong_vars}")
                return
            else:
                logger.info(f"bound check successfully")



            app_id = os.environ.get("SP_APP_ID")
            node_id = os.environ.get("SP_NODE_ID")
            g.Send_Vars["module_id"] = "/"+ app_id + "/" + node_id + "/" + "out1"
            g.Send_Vars["timestamp"] = str(datetime.now())[:-3]
            g.Send_Vars["module_name"] = "outlier-repair"

            logger.info(f"sent_var:{g.Send_Vars}")
            app.send({"checked_optimization_variable": g.Send_Vars})



    else:
        logger.info(f"Waiting params...")
        return

if __name__ == "__main__":
    suanpan.run(app)
