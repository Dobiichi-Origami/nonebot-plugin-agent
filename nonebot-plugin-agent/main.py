from nonebot import on_regex
from nonebot.internal.adapter import Event
from nonebot.params import RegexStr, RegexDict
import nonebot.params
from nonebot import logger

from .base import FunctionCaller, Tool
from .llm import OpenAIFunctionCallLLM

matcher = on_regex(".*")


def funcx(a: int, b: int) -> str:
    return str(int(a) + int(b))


llm = OpenAIFunctionCallLLM("your_key", "your_base")
tool = Tool(funcx,
            {
                "a": {"type": "string", "description": "number 1"},
                "b": {"type": "string", "description": "number 2"}
            },
            "used to sum 2 numbers in 1 number")


hashtable = {}


@matcher.handle()
async def handle(inputs = RegexStr(), event: Event = None):
    logger.info("进入")
    logger.info("这是输入: " + inputs)
    history = hashtable.get(event.get_user_id(), [])
    caller = FunctionCaller(llm, [tool], history)
    result, history, continuex = await caller(inputs)
    if continuex:
        logger.info("继续")
        hashtable[event.get_user_id()] = history
    else:
        logger.info("结束")
        hashtable[event.get_user_id()] = []
    await matcher.finish(result)


