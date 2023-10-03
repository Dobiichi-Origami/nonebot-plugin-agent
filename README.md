# nonebot-plugin-agent
此插件可帮助用户编写 Agent 插件或集成他人编写的插件，并添加至 Agent 中，帮助用户使用自然语言与你的插件生态进行交互

测试阶段目前支持私聊以及 @ 触发，请妥善管理好调用频率，以防你所使用的 LLM 服务商账户超消。后续集成用户黑白名单

Agent 默认不集成任何插件，安装支持 Agent 的插件的方式与普通插件一致。

如果你想自己编写插件，请调用 `Tool.add_to_tool_list` 函数。编写一个 Agent 插件的代码如下
```python
from nonebot import require
require("nonebot_plugin_agent")
from nonebot_plugin_agent.llm import Tool

def funcx(account: str, password: str) -> str:
    return str(len(account) + len(password))


Tool.add_to_tool_list(
    funcx,
    {
        "account": {"type": "string", "description": "user's steam account"},
        "password": {"type": "string", "description": "user's steam password"}
    },
    "this function helps user calculating their amount of games in steam library, needing account and password of steam"
)
```

其中： 
+ 第一个参数为一个 `Callable` 对象，支持异步与同步调用，返回值必须为一个 `str` 对象
+ 第二个参数为该 `Callable` 对象的形参参数 Schema，此处使用 [Json Schema 格式](https://json-schema.org/understanding-json-schema)
+ 第三个参数为该插件的介绍，用于帮助 LLM 更好的识别你的插件的用途

当你完成上述操作之后，便可以直接启动 Bot，此时插件已经注册到 Agent 中等待调用。
