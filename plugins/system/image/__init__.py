from nonebot import on_command, on_fullmatch
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from common.base.Depends import Arg, Img, Imgs
from common.base.Handle import register_handler
from plugins.system.image.utils import (
  add_images,
  delete_image,
  image_summary,
  update_image_database,
)

__plugin_meta__ = PluginMetadata(
  name="图片管理",
  description="图片管理",
  usage="""添加xx图片 [图片] / 删除图片 [图片]""",
  extra={
    "group": "系统",
  },
)

manager = on_command(
  "添加老婆",
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
)

delete = on_command("删除图片")

summary = on_fullmatch("图片统计")

update = on_fullmatch("更新图片")


async def manage_image(event: GroupMessageEvent, cmd=RawCommand(), imgs: list[str] = Imgs(), arg: str = Arg()):
  return await add_images(cmd=cmd, group_id=event.group_id, user_id=event.user_id, imgs=imgs, arg=arg)


async def delete_image_handler(event: Event, img: str = Img(required=True)):
  return await delete_image(user_id=int(event.get_user_id()), img=img)


async def summary_handler():
  return await image_summary()


async def update_handler():
  return await update_image_database()


register_handler(manager, manage_image)
register_handler(delete, delete_image_handler)
register_handler(summary, summary_handler)
register_handler(update, update_handler)
