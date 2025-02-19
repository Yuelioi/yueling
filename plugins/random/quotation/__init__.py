from nonebot import logger
from nonebot_plugin_alconna import Alconna, Args, MsgTarget, on_alconna

from common.Alc.Alc import pm, ptc, register_handler
from common.utils import get_random_image

__plugin_meta__ = pm(
  name="语录",
  description="语录",
  usage="""语录 [群友名]""",
  group="随机",
)


_quotation = Alconna("语录", Args["name?", str], meta=ptc(__plugin_meta__))
quotation = on_alconna(
  _quotation,
)


def quotation_handle(target: MsgTarget, name: str = ""):
  if target.private:
    return
  folder = "语录"

  white_list = ["玉米", "甜甜"]
  logger.info(f"生成语录: {name}")

  if name in white_list:
    random_file = get_random_image(folder, keyword=f"{name}")
  else:
    random_file = get_random_image(folder, keyword=f"{target.id}_{name}")

  if random_file:
    return random_file
  else:
    return "尚未添加该语录/上一条就是该语录"


register_handler(quotation, quotation_handle)
