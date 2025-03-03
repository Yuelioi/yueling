import random
import re
from typing import cast

from nonebot import on_message, require
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import Bot as BotV11
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata

from common.base.Permission import User_admin_validate

require("plugins.system.plugin")
from plugins.system.plugin.manager import hm

__plugin_meta__ = PluginMetadata(
  name="复读",
  description="基于一定规则重复群友的话",
  usage="""被动技能""",
  extra={
    "group": "娱乐",
  },
)


repeater = on_message()


shortest = 2  # 最短复读字符
shortest_times = 2  # 最短复读次数
banlist = [680653092, 761708854]  # 在机器人后面复读的 都禁言
last_message = {}
message_times = {}
whitelist = [48896449, 435826135]


@repeater.handle()
async def repeater_handler(
  bot: Bot,
  event: GroupMessageEvent,
):
  global last_message, message_times

  message, raw_message = _message_preprocess(event.get_plaintext())

  if not bot.adapter.get_name() == "OneBot V11":
    return

  botv11 = cast(BotV11, bot)
  eventV11 = cast(GroupMessageEvent, event)

  gid = str(event.group_id)
  uid = str(event.user_id)

  # 过滤其他插件
  extra_commands = ["语录", "表情", "火车"]
  for ban in extra_commands:
    if ban in raw_message:
      return

  for cmd in hm.commands.values():
    if raw_message in cmd.usage:
      return

  # 过滤链接
  if "http" in raw_message:
    return

  # 如果当前消息与记录消息不符合
  if message != last_message.get(gid):
    message_times[gid] = 1

  else:
    message_times[gid] += 1

  if message_times.get(gid) == shortest_times:
    await repeater.finish(raw_message)
  elif message_times.get(gid, 1) > shortest_times and gid in banlist:
    ranges = [
      (1, 5, 5),
      (6, 15, 20),
      (16, 45, 75),
      (46, 75, 75),
      (76, 85, 20),
      (86, 90, 5),
    ]
    award = ["SSR", "SR", "R", "R", "SR", "SSR"]

    random_range = random.choices(ranges, weights=[x[2] for x in ranges])[0]

    # 从选择的范围中随机生成一个整数
    random_num = random.randint(random_range[0], random_range[1])
    chosen_range_index = ranges.index(random_range)

    if uid in whitelist:
      return

    if await User_admin_validate(botv11, eventV11):
      await repeater.finish("不就是管理员么, 有什么了不起的!")
    await bot.set_group_ban(group_id=eventV11.group_id, user_id=eventV11.user_id, duration=random_num * 60)
    username = eventV11.sender.nickname
    await repeater.finish(f"恭喜{username}获得「{award[chosen_range_index]}级」禁言卡,将在{random_num}分钟后解禁")

  last_message[gid] = message


# 消息预处理
def _message_preprocess(message: str):
  raw_message = message
  images = re.findall(r"\[CQ:image.*?]", message)
  contained_images = {
    i: [
      re.findall(r"url=(.*?)[,\]]", i)[0][0],
      re.findall(r"file=(.*?)[,\]]", i)[0][0],
    ]
    for i in images
  }
  for i in contained_images:
    message = message.replace(i, f"[{contained_images[i][1]}]")

  return message, raw_message
