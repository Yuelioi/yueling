from nonebot import on_message
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata

from common.base.Depends import At
from plugins.funny.chat.utils import chat_ai

__plugin_meta__ = PluginMetadata(
  name="聊天功能",
  description="提供基础聊天功能",
  usage="""月灵 + 内容""",
  extra={"group": "娱乐"},
)


matcher = on_message()


@matcher.handle()
async def chat_handle(bot: Bot, event: GroupMessageEvent, at=At()):
  msg = event.get_plaintext()

  if (at and str(at) == bot.self_id) or msg.startswith("chat"):
    msg = event.get_plaintext()
    MSG = msg.replace("chat", "").strip()

    msg = chat_ai(MSG)

    # if msg:
    #   msg = await process_message(msg)
    #   msg = msg.strip()
    #   if len(msg) > 75:
    #     msg = MessageSegment.image(file=text_to_image(msg.split("\n")))

    await matcher.finish(msg)
