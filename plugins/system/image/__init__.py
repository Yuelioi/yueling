from nonebot.adapters import Event
from nonebot_plugin_alconna import (
  Alconna,
  Args,
  Arparma,
  Image,
  MsgTarget,
  MultiVar,
  on_alconna,
)
from nonebot_plugin_alconna.builtins.extensions.reply import ReplyMergeExtension

from common.Alc.Alc import pm, ptc, register_handler
from common.Alc.utils import get_source_command
from plugins.system.image.utils import (
  add_images,
  delete_image,
  image_summary,
  update_image_database,
)

__plugin_meta__ = pm(
  name="图片管理",
  description="图片管理",
  usage="""添加xx图片 [图片] / 删除图片 [图片]""",
  group="系统",
)

_manage = Alconna("添加老婆", Args["name?", str]["imgs", MultiVar(Image)], meta=ptc(__plugin_meta__))
manager = on_alconna(
  _manage,
  aliases={
    "添加老公",
    "添加福瑞",
    "添加龙图",
    "添加存档",
    "添加杂鱼",
    "添加表情",
    "添加美少女",
    "添加沙雕图",
    "添加语录",
    "添加吃的",
    "添加喝的",
    "添加玩的",
    "添加水果",
    "添加零食",
    "添加拍一拍",
  },
  extensions=[ReplyMergeExtension],
)

_delete = Alconna("删除图片", Args["img", Image])
delete_command = on_alconna(
  _delete,
  extensions=[ReplyMergeExtension],
)

_summary = Alconna("图片统计")
summary = on_alconna(_summary)

_update = Alconna("更新图片")
update = on_alconna(_update)


async def manage_image(result: Arparma, event: Event, target: MsgTarget, name: str = "", imgs: list[Image] = []):
  if target.private:
    return
  cmd = get_source_command(result)

  if not cmd:
    return

  return await add_images(cmd=cmd, group_id=target.id, user_id=event.get_user_id(), imgs=imgs, arg=name)


async def delete_image_handler(event: Event, img: Image):
  return await delete_image(user_id=int(event.get_user_id()), img=img)


async def summary_handler():
  return await image_summary()


async def update_handler():
  return await update_image_database()


register_handler(manager, manage_image)
register_handler(delete_command, delete_image_handler)
register_handler(summary, summary_handler)
register_handler(update, update_handler)
