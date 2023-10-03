import asyncio
import datetime
import json
from typing import List, AnyStr, Callable, Optional, Any, Dict

from nonebot import logger

from .action import BaseAction, ToolAction, FinalAction, LLMAction, HumanAction
from .llm import Tool, LLM_Type, OpenAIFunctionCallLLM


def async_wrapper(func: Callable) -> Callable:
    async def new_async_wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return new_async_wrapper


def convert_result_into_str(result: Any) -> AnyStr:
    if isinstance(result, str):
        return result
    elif isinstance(result, bytes):
        return str(result, encoding="utf8")
    elif hasattr(result, "__str__"):
        return result.__str__
    else:
        return json.dumps(result, ensure_ascii=False)


class FunctionCaller:
    def __init__(
            self,
            llm_type: str = LLM_Type.OPENAI,
            max_calling_round: Optional[int] = 10,
            max_timeout_in_seconds: Optional[int] = 10,
            **kwargs
    ):
        if llm_type == LLM_Type.OPENAI:
            llm = OpenAIFunctionCallLLM(**kwargs)
        else:
            raise TypeError("不支持的 LLM 类型")

        self.function_call_llm = llm
        self.max_calling_round = max_calling_round
        self.max_timeout_in_seconds = max_timeout_in_seconds
        self.history_messages: Dict[AnyStr, List[BaseAction]] = {}

    async def process_with_tool(
            self,
            user_id: AnyStr,
            user_input: AnyStr,
            **kwargs,
    ) -> AnyStr:
        calling_round = 0
        start_timestamp = datetime.datetime.now()
        tools = Tool.get_tool_list()
        intermedia_actions = self.history_messages.get(user_id, [])
        intermedia_actions.append(HumanAction(question=user_input))

        try:
            while calling_round <= self.max_calling_round \
                    and (datetime.datetime.now() - start_timestamp).seconds <= self.max_timeout_in_seconds:
                next_action: BaseAction = await self.function_call_llm.async_generate_next_action(
                    tools=tools,
                    intermedia_actions=intermedia_actions,
                    inputs=user_input,
                )

                intermedia_actions.append(next_action)
                if isinstance(next_action, FinalAction):
                    return next_action.return_val
                elif isinstance(next_action, LLMAction):
                    return next_action.reply
                elif isinstance(next_action, ToolAction):
                    tool_need_for_calling = tools[next_action.tool_name].function
                    if asyncio.iscoroutinefunction(tool_need_for_calling):
                        func = tool_need_for_calling
                    else:
                        func = async_wrapper(tool_need_for_calling)
                    tool_result = await func(**next_action.tool_arg)
                    logger.info("工具 {} 输出: ".format(next_action.tool_name) + tool_result)
                    intermedia_actions[-1].tool_result = tool_result

                calling_round += 1

            return "等待超时或重试轮次过多"
        finally:
            logger.info("保存历史信息")
            self.history_messages[user_id] = intermedia_actions[-10:]

    async def __call__(self, *args, **kwargs):
        return await self.process_with_tool(*args, **kwargs)



