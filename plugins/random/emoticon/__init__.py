import random
from pathlib import Path

from nonebot_plugin_alconna import AlconnaMatcher, Arparma, UniMessage, on_alconna

from common.Alc.Alc import msg, pm, ptc, register_handler
from common.utils import get_random_images

__plugin_meta__ = pm(
  name="表情包",
  description="查询表情包",
  usage="""发送: 空格 + [关键词]/n 查询:2个空格[关键词]""",
  group="随机",
)


meta = ptc(__plugin_meta__)

_emoticon = msg()
_emoticon.meta = ptc(__plugin_meta__)
emoticon = on_alconna(_emoticon, priority=0)


@emoticon.handle()
async def emoticon_handle(result: Arparma, matcher: AlconnaMatcher):
  cmd = ""
  args = ""
  text = str(result.origin)

  if text.startswith("  "):
    cmd = "查询表情"
    args = text.split("  ")[1]
  elif text.startswith(" "):
    cmd = "表情"
    args = text.split(" ")[1]
  else:
    return

  if not args:
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
      await emoticon.send(UniMessage.image(path=random.choice(matching_files)))

    matcher.stop_propagation()
