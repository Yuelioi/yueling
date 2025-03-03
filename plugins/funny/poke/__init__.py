import random

from nonebot import on_notice
from nonebot.adapters.onebot.v11 import Bot, MessageSegment, PokeNotifyEvent
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import MsgTarget

from common.utils import get_random_image

__plugin_meta__ = PluginMetadata(
  name="戳一戳",
  description="戳一戳月灵反馈",
  usage="""戳一戳月灵""",
  extra={"group": "娱乐"},
)


user_data = {}

pk = on_notice()


@pk.handle()
async def poke_detect(bot: Bot, target: MsgTarget, event: PokeNotifyEvent):
  """戳一戳事件监听"""

  if target.private:
    return random.choice(
      [
        "戳什么戳?",
        "别戳啦!!",
      ]
    )
  group_id = event.group_id if event.group_id else 0
  if str(event.target_id) == bot.self_id:
    target_info = await bot.get_group_member_info(group_id=group_id, user_id=event.user_id)
    nickname = target_info.get("nickname", "")
    await pk.finish(f"姓{nickname[0]}的,你戳什么戳!")

  img_folder = "拍一拍"
  if matching_file := get_random_image(img_folder, str(event.target_id)):
    await pk.finish(MessageSegment.image(matching_file))
