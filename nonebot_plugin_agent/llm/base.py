import enum
from abc import ABC, abstractmethod
from copy import deepcopy

from typing import AnyStr, List, Callable, Dict, Any, Optional
from ..action import BaseAction


class Tool:

    _tool_maps: Dict = {}

    def __init__(
            self,
            function: Callable,
            param_list: Dict[AnyStr, Any],
            description: Optional[AnyStr],
    ):
        self.name = function.__name__
        self.function = function
        self.param_list = param_list
        self.description = description
        self.required = []

    @classmethod
    def add_to_tool_list(
        cls,
        function: Callable,
        param_list: Dict[AnyStr, Any],
        description: Optional[AnyStr],
    ):
        t = Tool(function, param_list, description)
        cls._tool_maps[t.name] = t

    @classmethod
    def get_tool_list(cls) -> Dict:
        return deepcopy(cls._tool_maps)


class LLM_Type:
    OPENAI = "openai"


class BaseFunctionCallLLM(ABC):
    @abstractmethod
    async def async_generate_next_action(
            self,
            tools: Dict[AnyStr, Tool],
            intermedia_actions: List[BaseAction],
            inputs: AnyStr
    ) -> BaseAction:
        ...


