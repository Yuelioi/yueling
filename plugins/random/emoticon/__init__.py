import random
from pathlib import Path

from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.matcher import Matcher
from nonebot.plugin import PluginMetadata

from common.base.Depends import Ats
from common.utils import get_random_images

__plugin_meta__ = PluginMetadata(
  name="表情包",
  description="查询表情包",
  usage="""发送: 空格 + [关键词]/n 查询:2个空格[关键词]""",
  extra={
    "group": "随机",
  },
)


emoticon = on_message()


@emoticon.handle()
async def emoticon_handle(event: GroupMessageEvent, matcher: Matcher, ats=Ats(0, 0)):
  cmd = ""
  args = ""
  text = event.get_plaintext()

  if len(ats):
    return

  if text == "表情":
    cmd = "表情"
    args = None
  elif text.startswith("   "):
    return
  elif text.startswith("  "):
    cmd = "查询表情"
    args = text.split("  ")[1]
  elif text.startswith(" "):
    cmd = "表情"
    args = text.split(" ")[1]
  else:
    return

  img_folder = "表情"

  matching_files = get_random_images(img_folder, args)
  if not matching_files:
    return

  if matching_files:
    if cmd == "查询表情":
      matching_files = [Path(file).stem for file in matching_files]
      await emoticon.send(f"共找到{len(matching_files)}个:" + "\n".join(matching_files[:10]))
    elif cmd == "表情":
      await emoticon.send(MessageSegment.image(file=random.choice(matching_files)))

    matcher.stop_propagation()
