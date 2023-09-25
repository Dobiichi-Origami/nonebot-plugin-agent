import json

from nonebot import on_regex
from nonebot.internal.adapter import Event
from nonebot.params import RegexStr, RegexDict
import nonebot.params
from nonebot import logger

from .base import FunctionCaller, Tool
from .llm import OpenAIFunctionCallLLM

matcher = on_regex(".*")


def funcx(account: str, password: str) -> str:
    return str(len(account) + len(password))


llm = OpenAIFunctionCallLLM("your_api_key", "your_base")
tool = Tool(funcx,
            {
                "account": {"type": "string", "description": "user's steam account"},
                "password": {"type": "string", "description": "user's steam password"}
            },
            "this function helps user calculating their amount of games in steam library, needing account and password of steam")


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
    else:
        logger.info("结束")

    hashtable[event.get_user_id()] = history[-10:]
    await matcher.finish(result)


