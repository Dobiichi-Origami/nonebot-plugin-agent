import json
import os

from openai import ChatCompletion
from nonebot import logger

from .base import BaseFunctionCallLLM, Tool
from typing import AnyStr, Optional, List, Any, Tuple, Dict
from ..action import BaseAction, ToolAction, HumanAction, LLMAction, FinalAction

_CHOICES = 'choices'
_FINISH_REASON = "finish_reason"
_MESSAGE = "message"
_FUNCTION_CALL = "function_call"

_STATUS_FUNCTION_CALL = "function_call"
_STATUS_STOP = "stop"


class OpenAIFunctionCallLLM(BaseFunctionCallLLM):
    def __init__(
            self,
            open_api_key: Optional[AnyStr] = None,
            open_api_base: Optional[AnyStr] = None,
            open_api_model: Optional[AnyStr] = "gpt-3.5-turbo-0613",
            **kwargs
    ):
        self.api_key = open_api_key if open_api_key else os.environ.get("OPENAI_API_KEY")
        self.api_base = open_api_base if open_api_base \
            else os.environ.get("OPENAI_API_BASE") if os.environ.get("OPENAI_API_BASE") else None
        self.api_model = open_api_model

    async def async_generate_next_action(
            self,
            tools: Dict[AnyStr, Tool],
            intermedia_actions: List[BaseAction],
            inputs: AnyStr
    ) -> BaseAction:
        tool_list = self.__class__._get_tool_list(tools)
        history_messages = self.__class__._get_message(intermedia_actions)

        logger.info("发送信息:" + json.dumps(history_messages, ensure_ascii=False))
        response = await self._get_chat_completion(messages=history_messages, functions=tool_list)
        logger.info("OpenAI 回复: " + json.dumps(response, ensure_ascii=False))

        message = response[_CHOICES][0]
        status = message[_FINISH_REASON]
        result = message[_MESSAGE]["content"]

        if status == _STATUS_FUNCTION_CALL:
            call_info = message[_MESSAGE][_FUNCTION_CALL]
            if len(call_info["arguments"]) != 0:
                return ToolAction(tool_name=call_info["name"], tool_arg=json.loads(call_info["arguments"]))
            else:
                return LLMAction(reply=result)
        elif status == _STATUS_STOP:
            if await self._check_is_problem_solved(inputs, result):
                return FinalAction(return_val=result)
            else:
                return LLMAction(reply=result)
        else:
            return FinalAction(return_val="error")

    async def _check_is_problem_solved(self, inputs: AnyStr, answer: AnyStr) -> bool:
        messages = [
            {
                "role": "system",
                "content": """
                your duty is to check whether user's question has benn answered.
                If question has been answered, you should and only should answer "YES", no spare word.
                Similarly, answer "NO" only if the question remains unresolved.
                """,
            },
            {
                "role": "user",
                "content": """
                there is a conversation below, you need to tell whether the question has beem answered.
                
                question: {inputs}
                answer: {answer},
                
                Next, give your judgement:
                """.format(inputs=inputs, answer=answer),
            },
        ]

        message: str = (await self._get_chat_completion(messages=messages))[_CHOICES][0][_MESSAGE]["content"]
        logger.info("检查信息发送: " + message)
        return message.upper() == "YES"

    async def _get_chat_completion(self, **kwargs):
        return await ChatCompletion.acreate(
            api_key=self.api_key,
            api_base=self.api_base,
            model=self.api_model,
            **kwargs
        )

    @staticmethod
    def _get_tool_list(tools: Dict[AnyStr, Tool]) -> List[Dict[AnyStr, Any]]:
        result: List[Dict[AnyStr, Any]] = []
        for tool_name, tool in tools.items():
            result.append({
                "name": tool_name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": tool.param_list
                },
                "required": tool.required
            })
        return result

    @staticmethod
    def _get_message(
            intermedia_actions: List[BaseAction],
            prompt: Optional[AnyStr] = None
    ) -> List[Dict[AnyStr, AnyStr]]:
        prompt = prompt if prompt else "you are a helpful assistant, you need to use function to solve people' question"
        messages = [{"role": "system", "content": prompt}]
        for action in intermedia_actions:
            if isinstance(action, ToolAction):
                messages.append({
                    "role": "function",
                    "name": action.tool_name,
                    "content": action.tool_result,
                })
            elif isinstance(action, HumanAction):
                messages.append({
                    "role": "user",
                    "content": action.content,
                })
            elif isinstance(action, LLMAction):
                messages.append({
                    "role": "assistant",
                    "content": action.reply
                })
            elif isinstance(action, FinalAction):
                messages.append({
                    "role": "assistant",
                    "content": action.return_val
                })
            else:
                raise TypeError("未知的 Action 类型: " + str(type(action)))
        return messages
