from abc import ABC, abstractmethod

from typing import AnyStr, List, Callable, Tuple, Dict, Any, Optional
from ..action import BaseAction, FinalAction, ToolAction


class Tool:
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


class BaseFunctionCallLLM(ABC):
    @abstractmethod
    async def async_generate_next_action(
            self,
            tools: Dict[AnyStr, Tool],
            intermedia_actions: List[BaseAction],
            inputs: AnyStr
    ) -> BaseAction:
        ...


