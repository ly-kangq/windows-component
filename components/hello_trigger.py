import suanpan
from suanpan.app import app
from suanpan.app.arguments import Int, Float, Bool
from suanpan.app.loops import IntervalIndex

DEFAULT_INTERVAL = 5
loop = IntervalIndex(DEFAULT_INTERVAL)


@app.trigger.afterInit
def initTrigger(context):
    args = context.args
    loop.set(seconds=10, pre=args.pre, disabled=args.disabled)


@app.trigger.loop(loop)
@app.trigger.output(Int(key="outputData1", alias="index"))
@app.trigger.param(Float(key="param1", alias="seconds", default=DEFAULT_INTERVAL))
@app.trigger.param(Bool(key="param2", alias="pre", default=False))
@app.trigger.param(Bool(key="param3", alias="disabled", default=False))
def SPTrigger(context, n):
    return n


if __name__ == "__main__":
    suanpan.run(app)