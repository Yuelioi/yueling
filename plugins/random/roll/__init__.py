import random
import re

from nonebot import on_command
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.plugin import PluginMetadata

from common.base.Depends import Args

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
  usage="""roll 整数 | 整数 整数 | x y z...""",
  extra={
    "group": "随机",
  },
)


random_cmd = on_command("roll")


@random_cmd.handle()
async def random_roll(event: Event, args: list[str] = Args()):
  if len(args) > 1:
    if all(re.match(r"^-?\d+$", arg) for arg in args):
      count = int(args[0])
      sides = int(args[1])
      if count > 30:
        count = 30

      msg = random.sample(range(1, sides + 1), count)
      msg = f"你roll到的数组是{msg!s}"
    else:
      msg = random.choice(random_reply_list).format(random.choice(args))
  #
  else:
    if args[0].isdigit():
      msg = random.randint(1, int(args[0]))
      msg = f"您roll到的数字是「{random.randint(0, int(args[0]))}」"
    else:
      msg = "请输入正确的指令(整数 | 整数 整数 | x y z)"

  await random_cmd.finish(MessageSegment.at(event.get_user_id()) + msg)
