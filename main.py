import nonebot
from nonebot.adapters.console import Adapter as ConsoleAdapter  # 避免重复命名

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(ConsoleAdapter)

nonebot.load_plugins("nonebot-plugin-agent")  # 本地插件

if __name__ == "__main__":
    nonebot.run()