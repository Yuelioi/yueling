from nonebot_plugin_alconna import Alconna, Args, on_alconna

from common.Alc.Alc import pm, ptc, register_handler
from plugins.random.rename.data_source import group_change_name

__plugin_meta__ = pm(
  name="随机取名",
  description="随机取群昵称",
  usage="""随机取名""",
  group="随机",
)

_rename = Alconna("随机取名", Args["name?", str], meta=ptc(__plugin_meta__))
rename = on_alconna(_rename)

register_handler(rename, group_change_name)
