import asyncio
import datetime
import json
from typing import List, AnyStr, Callable, Tuple, Optional, Any
from .action import BaseAction, ToolAction, FinalAction, LLMAction
from .llm import BaseFunctionCallLLM, Tool


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
            llm: BaseFunctionCallLLM,
            tool_set: List[Tool],
            intermedia_actions: Optional[List[BaseAction]] = None,
            max_calling_round: Optional[int] = 10,
            max_timeout_in_seconds: Optional[int] = 10,
    ):
        self.function_call_llm = llm
        self.tool_set = {tool.name: tool for tool in tool_set}
        self.max_calling_round = max_calling_round
        self.max_timeout_in_seconds = max_timeout_in_seconds
        self.intermedia_actions = intermedia_actions

    async def process_with_tool(
            self,
            user_input: AnyStr,
    ) -> (AnyStr, List[BaseAction], bool):
        calling_round = 0
        start_timestamp = datetime.datetime.now()
        while calling_round <= self.max_calling_round \
                and (datetime.datetime.now() - start_timestamp).seconds <= self.max_timeout_in_seconds:
            next_action: BaseAction = await self.function_call_llm.async_generate_next_action(
                tools=self.tool_set,
                intermedia_actions=self.intermedia_actions,
                inputs=user_input,
            )

            if isinstance(next_action, FinalAction):
                return next_action.return_val, self.intermedia_actions, True
            elif isinstance(next_action, LLMAction):
                return next_action.reply, self.intermedia_actions, False
            elif isinstance(next_action, ToolAction):
                tool_need_for_calling = self.tool_set[next_action.tool_name]
                if asyncio.iscoroutinefunction(tool_need_for_calling):
                    func = tool_need_for_calling.function
                else:
                    func = async_wrapper(tool_need_for_calling.function)

                tool_result = await func(**next_action.tool_arg)
                next_action.tool_result = tool_result
                self.intermedia_actions.append(next_action)

            calling_round += 1
        return "等待超时或重试轮次过多", [], False

    async def __call__(self, *args, **kwargs):
        return await self.process_with_tool(*args, **kwargs)



