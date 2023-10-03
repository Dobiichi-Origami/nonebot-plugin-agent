from nonebot.plugin import PluginMetadata
from .config import AgentConfig

__plugin_meta__ = PluginMetadata(
    name="Nonebot Agent",
    description="适配你的插件，让 LLM 来为你处理用户调用",
    usage="见 README.md",
    type="application",
    config=AgentConfig,
    homepage="https://github.com/Dobiichi-Origami/nonebot-plugin-agent#nonebot-plugin-agent",
)

from .action import *
from .llm import *
from .base import FunctionCaller


__all__ = [
    "BaseAction",
    "HumanAction",
    "ToolAction",
    "LLMAction",
    "FinalAction",
    "BaseFunctionCallLLM",
    "Tool",
    "LLM_Type",
    "FunctionCaller",
]

from nonebot import get_driver, logger, on_message
from nonebot.internal.adapter import Event
from nonebot.params import EventPlainText
from nonebot.rule import to_me


config = AgentConfig.parse_obj(get_driver().config)
caller = FunctionCaller(
    config.agent_llm_type,
    config.agent_max_calling_round_per_query,
    config.agent_max_timeout_in_seconds_per_request,
    **config.agent_llm_kwargs
)

logger.info("Agent 配置参数: " + str(config))

matcher = on_message(rule=to_me(), priority=100)


@matcher.handle()
async def handle(inputs=EventPlainText(), event: Event = None):
    logger.info("进入 agent 逻辑，用户输入: " + inputs)
    result = await caller(event.get_user_id(), inputs)
    logger.info("LLM 返回: " + result)

    await matcher.finish(result)
