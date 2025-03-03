from nonebot import logger, on_command
from nonebot.params import CommandArg
from nonebot_plugin_alconna import Alconna, Args, Arparma, Match, MsgTarget, UniMessage, on_alconna

from common.Alc.Alc import pm, ptc, register_handler
from common.utils import get_random_image

__plugin_meta__ = pm(
  name="语录",
  description="语录",
  usage="""语录 [群友名]""",
  group="随机",
)


_quotation = Alconna("语录", Args["name?", str], meta=ptc(__plugin_meta__))
quotation = on_alconna(_quotation)


@quotation.handle()
async def quotation_handle(target: MsgTarget, name: Match[str], result: Arparma):
  if target.private:
    return

  nickname = result.main_args.get("name") if result.main_args else ""
  print(result)
  print(result.main_args.get("name"))
  print(nickname)

  if name.available:
    nickname = name.result
  folder = "语录"

  white_list = ["玉米", "甜甜"]
  logger.info(f"生成语录: {name}")

  if name in white_list:
    random_file = get_random_image(folder, keyword=f"{nickname}")
  else:
    random_file = get_random_image(folder, keyword=f"{target.id}_{nickname}")

  if random_file:
    await quotation.finish(UniMessage.image(path=random_file))
  else:
    await quotation.finish("尚未添加此人语录")


# register_handler(quotation, quotation_handle)
