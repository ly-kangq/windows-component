import suanpan
from flask import Flask, request, render_template
from suanpan import g
from suanpan.app import app
from suanpan.log import logger
from suanpan.utils import json
from suanpan.storage import storage
from suanpan.app.arguments import String, Json


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
    # create and configure the app
    web = Flask(__name__)

    # a simple page that says hello
    @web.route('/')
    def hello():
        return render_template('pure.html')

    # set some parameters and save to oss
    @web.route('/params', methods=['POST'])
    def params():
        params = request.get_json()
        logger.info(f'set new params: {params}')

        # 存储配置到oss，组件重启之后可以load
        saveParams(params)

        # 存储临时变量到 g，可以和消息事件共享
        g.someParameter = params

        return {'message': 'ok', 'code': 0}

    return web


def runFlask():
    # 初始化一个 flask
    web = create_app()
    # flask 由 suanpan app 加载
    app._stream.sioLoop.setWebApp(web)


@app.afterInit
def afterInit(context):
    try:
        # 组件初始化，从oss读取保存的参数配置
        g.someParameter = loadParams()
    except:
        pass

    # 在sdk中运行flask，会自动分配端口
    runFlask()


@app.input(Json(key="inputData1", alias="user_text", default="Suanpan"))
@app.param(String(key="param_prefix", alias="prefix"))
@app.output(Json(key="outputData1", alias="result"))
def hello_flask(context):
    args = context.args
    logger.info(f'hello flask {args}')
    logger.info(f'hello paramse {g.someParameter}')
    return f'Hello Flask, {args.prefix} {args.user_text} {g.someParameter}!'


if __name__ == "__main__":
    suanpan.run(app)
