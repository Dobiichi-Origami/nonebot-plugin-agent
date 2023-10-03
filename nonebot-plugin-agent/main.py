from nonebot import on_message
from nonebot.internal.adapter import Event
from nonebot.params import EventPlainText
from nonebot.rule import to_me
from nonebot import logger

from .base import FunctionCaller, Tool
from .llm import LLM_Type

matcher = on_message(rule=to_me(), priority=100)


# def funcx(account: str, password: str) -> str:
#     return str(len(account) + len(password))
#
#
# Tool.add_to_tool_list(
#     funcx,
#     {
#         "account": {"type": "string", "description": "user's steam account"},
#         "password": {"type": "string", "description": "user's steam password"}
#     },
#     "this function helps user calculating their amount of games in steam library, needing account and password of steam"
# )


@matcher.handle()
async def handle(inputs=EventPlainText(), event: Event = None):
    logger.info("进入 agent 逻辑，用户输入: " + inputs)
    caller = FunctionCaller(LLM_Type.OPENAI)
    result = await caller(event.get_user_id(), inputs)
    logger.info("LLM 返回: " + result)

    await matcher.finish(result)


