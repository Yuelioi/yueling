import random
import re
from io import BytesIO

from nonebot import on_command
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.plugin import PluginMetadata
from PIL import Image, ImageSequence

from common.base.Depends import Args, Img
from common.base.Handle import register_handler
from common.utils import api

random_reply_list = [
  "emmm,要不试试「{}」",
  "来试试「{}」吧",
  "月灵觉得「{}」不错哟~",
  "就决定是你了!「{}」!",
  "月灵想要「{}」!",
]


__plugin_meta__ = PluginMetadata(
  name="roll",
  description="roll 点",
  usage="""roll 整数 | 整数 整数 | x y z...| GIF""",
  extra={"group": "随机", "commands": ["roll"]},
)


random_cmd = on_command("roll")


async def random_handler(event: Event, args: list[str] = Args(0), img: str = Img(required=False)):
  at = MessageSegment.at(event.get_user_id())
  if img:
    data = await api.fetch_image_from_url_ssl(img)
    gif = Image.open(data)
    if gif.format != "GIF":
      return "只支持GIF格式图片"
    total_frames = getattr(gif, "n_frames", 1)
    target_frame = random.randint(0, total_frames - 1)
    gif.seek(target_frame)
    output = BytesIO()
    gif.save(output, format="PNG")
    return at + MessageSegment.image(file=output)

  if not args:
    return

  if len(args) > 1:
    if all(re.match(r"^-?\d+$", arg) for arg in args):
      count = int(args[0])
      sides = int(args[1])
      if count > 30:
        count = 30

      msg = random.sample(range(1, sides + 1), count)
      return at + f"你roll到的数组是{msg!s}"
    else:
      return at + random.choice(random_reply_list).format(random.choice(args))
  #
  else:
    if args[0].isdigit():
      msg = random.randint(1, int(args[0]))
      return at + f"您roll到的数字是「{random.randint(0, int(args[0]))}」"
    else:
      return at + "请输入正确的指令(整数 | 整数 整数 | x y z)"


register_handler(random_cmd, random_handler)
