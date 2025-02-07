from nonebot_plugin_alconna import on_alconna

from common.Alc.Alc import arg, pm, ptc, register_handler
from plugins.random.rename.data_source import group_change_name

__plugin_meta__ = pm(
  name="随机取名",
  description="随机取群昵称",
  usage="""随机取名""",
  group="随机",
)

_rename = arg("随机取名", type=str, required=False, meta=ptc(__plugin_meta__))
rename = on_alconna(_rename)

register_handler(rename, group_change_name)
