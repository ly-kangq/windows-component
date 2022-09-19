import time
import suanpan
from suanpan.app import app
from suanpan.app.arguments import String, Json


@app.trigger.interval(2)
@app.param(String(key="prefix", alias="prefix"))
@app.trigger.output(Json(key="outputData1"))
def hello_trigger(context):
    args = context.args
    return f'hello trigger, {args.prefix} @ {time.time()}'


if __name__ == "__main__":
    suanpan.run(app)
