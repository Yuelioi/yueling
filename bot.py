import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)


__import__("bootstrap")
nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_from_toml("pyproject.toml")
nonebot.load_builtin_plugins("echo")
# __import__("server")


if __name__ == "__main__":
  nonebot.run()
