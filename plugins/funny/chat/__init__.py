from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.plugin import PluginMetadata

from common.base.Depends import Args
from common.utils.content_convert import text_to_image
from plugins.funny.chat.utils import chat_ai, process_message

__plugin_meta__ = PluginMetadata(
  name="聊天功能",
  description="提供基础聊天功能",
  usage="""月灵 + 内容""",
  extra={"group": "娱乐"},
)


matcher = on_command("chat")


@matcher.handle()
async def chat_handle(args=Args(1, 99)):
  content = " ".join(args)

  msg = chat_ai(content)

  if msg:
    msg = await process_message(msg)
    msg = msg.strip()
    if len(msg) > 75:
      msg = MessageSegment.image(file=text_to_image(msg.split("\n")))

  await matcher.finish(msg)
