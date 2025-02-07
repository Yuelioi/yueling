import random

from nonebot import get_driver
from nonebot.adapters import Event
from nonebot_plugin_alconna import Arparma, UniMessage, on_alconna

from common.Alc.Alc import args, pm, ptc, register_handler
from common.utils import text_to_image
from plugins.funny.chat.utils import chat_ai, fetch_chat_response, process_message

__plugin_meta__ = pm(
  name="聊天功能",
  description="提供基础聊天功能",
  usage="""月灵 + 内容""",
  group="娱乐",
)

_chat = args("月灵", required=False, meta=ptc(__plugin_meta__))
chat = on_alconna(_chat, aliases={"那我问你", "chat"})


async def chat_handle(event: Event, arp: Arparma, args: list[str] = []):
  userid = event.get_user_id()

  at_reply = ["我在呐~", "干神马！"]
  at_super_reply = ["我在呐~", "我在呐~"]
  config = get_driver().config

  if not args:
    if str(userid) in config.superusers:
      msg = random.choice(at_super_reply)
    else:
      msg = random.choice(at_reply)
    return msg

  content = " ".join(args)

  msg = ""

  if "那我问你" in arp.header_match.origin or "chat" in arp.header_match.origin:
    msg = chat_ai(content)
  else:
    msg = await fetch_chat_response(content)

    if msg:
      msg = await process_message(msg)
      msg = msg.strip()
      if len(msg) > 75:
        msg = UniMessage.image(raw=text_to_image(msg.split("\n")))

  return msg


register_handler(chat, chat_handle)
