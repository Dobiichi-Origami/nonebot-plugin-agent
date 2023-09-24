from typing import AnyStr, Dict, Any, Optional


class BaseAction:
    def __init__(self, log: Optional[AnyStr] = None):
        self.log = log


class HumanAction(BaseAction):
    def __init__(self, question: AnyStr, **kwargs):
        super().__init__(**kwargs)
        self.content = question


class ToolAction(BaseAction):
    def __init__(self, tool_name: AnyStr, tool_arg: Dict[AnyStr, Any], **kwargs):
        super().__init__(**kwargs)
        self.tool_name = tool_name
        self.tool_arg = tool_arg
        self.tool_result = ""


class LLMAction(BaseAction):
    def __init__(self, reply: AnyStr, **kwargs):
        super().__init__(**kwargs)
        self.reply = reply


class FinalAction(BaseAction):
    def __init__(self, return_val: AnyStr, **kwargs):
        super().__init__(**kwargs)
        self.return_val = return_val
