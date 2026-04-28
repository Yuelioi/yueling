"""Roll 点 / 随机选择 — 核心函数 + 双入口"""

import random
import re
from io import BytesIO

from nonebot import on_command
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.plugin import PluginMetadata
from PIL import Image

from core.deps import Args, Img
from core.handler import register_handler
from services.external_api import fetch_image_from_url_ssl
from core.context import ToolContext

__plugin_meta__ = PluginMetadata(
  name="roll",
  description="roll 点 / 随机选择",
  usage="""roll 整数 | 整数 整数 | x y z...| GIF""",
  extra={
    "group": "随机",
    "commands": ["roll"],
    "tools": [{
      "name": "roll_dice",
      "description": "掷骰子、随机选择、或从GIF中随机抽取一帧(需要附带GIF图片)",
      "tags": ["fun", "random", "image"],
      "examples": ["roll 100", "帮我选吃火锅还是烧烤", "随机一个1到6", "帮我roll下这个GIF"],
      "parameters": {
        "max_value": {"type": "integer", "description": "最大值(掷骰子时)", "default": 100},
        "options": {"type": "string", "description": "用空格分隔的选项(二选一时)", "default": ""},
      },
      "handler": "roll_tool_handler",
    }],
  },
)

REPLY_TEMPLATES = [
  "emmm,要不试试「{}」",
  "来试试「{}」吧",
  "月灵觉得「{}」不错哟~",
  "就决定是你了!「{}」!",
  "月灵想要「{}」!",
]


# ─── 核心函数 ─────────────────────────────────────────────


def do_roll(max_value: int = 100) -> int:
  """掷骰子"""
  return random.randint(1, max(1, max_value))


def do_roll_multi(count: int, sides: int) -> list[int]:
  """掷多个骰子"""
  count = min(count, 30)
  if count > sides:
    raise ValueError("数量不能大于面数")
  return random.sample(range(1, sides + 1), count)


def do_choose(options: list[str]) -> str:
  """从选项中随机选一个"""
  choice = random.choice(options)
  template = random.choice(REPLY_TEMPLATES)
  return template.format(choice)


async def do_gif_frame(image_url: str) -> BytesIO:
  """从 GIF 中随机抽一帧"""
  data = await fetch_image_from_url_ssl(image_url)
  gif = Image.open(data)
  if gif.format != "GIF":
    raise ValueError("只支持GIF格式图片")
  total_frames = getattr(gif, "n_frames", 1)
  gif.seek(random.randint(0, total_frames - 1))
  output = BytesIO()
  gif.save(output, format="PNG")
  output.seek(0)
  return output


# ─── NoneBot 命令入口 ─────────────────────────────────────


random_cmd = on_command("roll")


async def random_handler(event: Event, args: list[str] = Args(0), img: str = Img(required=False)):
  at = MessageSegment.at(event.get_user_id())

  if img:
    try:
      output = await do_gif_frame(img)
      return at + MessageSegment.image(file=output)
    except ValueError as e:
      return str(e)

  if not args:
    return

  if len(args) > 1:
    if all(re.match(r"^-?\d+$", arg) for arg in args):
      try:
        result = do_roll_multi(int(args[0]), int(args[1]))
        return at + f"你roll到的数组是{result!s}"
      except ValueError as e:
        return at + str(e)
    else:
      return at + do_choose(args)
  else:
    if args[0].isdigit():
      return at + f"您roll到的数字是「{do_roll(int(args[0]))}」"
    else:
      return at + "请输入正确的指令(整数 | 整数 整数 | x y z)"


register_handler(random_cmd, random_handler)


# ─── AI Tool 入口 ─────────────────────────────────────────


async def roll_tool_handler(ctx: ToolContext, max_value: int = 100, options: str = "") -> str:
  # 如果有图片，尝试 GIF 抽帧
  imgs = ctx.get_images()
  if imgs:
    try:
      output = await do_gif_frame(imgs[0])
      from nonebot.adapters.onebot.v11 import MessageSegment
      return MessageSegment.image(file=output)
    except ValueError as e:
      return str(e)

  if options:
    items = [o.strip() for o in options.split() if o.strip()]
    if items:
      return do_choose(items)
  return f"🎲 {do_roll(max_value)}"
