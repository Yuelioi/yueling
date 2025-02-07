import nonebot

# from nonebot.adapters import Adapter, Event
from nonebot.adapters.discord import Adapter as DISCORD_ADAPTER
from nonebot.adapters.kaiheila import Adapter as KAIHEILA_ADAPTER
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

# from nonebot.message import event_preprocessor
# from nonebot_plugin_alconna import AlconnaMatcher

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)
# driver.register_adapter(DISCORD_ADAPTER)
# driver.register_adapter(KAIHEILA_ADAPTER)

__import__("bootstrap")
nonebot.load_plugin("nonebot_plugin_alconna")
nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_from_toml("pyproject.toml")
nonebot.load_builtin_plugins("echo")
# __import__("server")


# @event_preprocessor
# async def _something(event: Event, matcher: Adapter):
#   print(matcher.get_name())


# @event_postprocessor
# async def do_something(event: Event):
#   pass


if __name__ == "__main__":
  nonebot.run()
