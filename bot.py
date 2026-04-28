import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

import core.lifecycle  # noqa: E402, F401

nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_from_toml("pyproject.toml")

nonebot.load_plugin("plugins.ai_dispatch")

if __name__ == "__main__":
  nonebot.run()
