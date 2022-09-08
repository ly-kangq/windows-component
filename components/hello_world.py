import suanpan
from suanpan.app import app
from suanpan.app.arguments import String, Json


@app.input(Json(key="inputData1", alias="user_text", default="Suanpan"))
@app.param(String(key="param_prefix", alias="prefix"))
@app.output(Json(key="outputData1", alias="result"))
def hello_world(context):
    args = context.args
    return f'Hello World, {args.prefix} {args.user_text}!'


if __name__ == "__main__":
    suanpan.run(app)
