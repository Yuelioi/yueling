import random
from typing import cast

from nonebot import on_message
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import Bot as BotV11
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule

from core.permission import is_admin
from core.config import get_plugin_config
from plugins.system.plugin.manager import hm

__plugin_meta__ = PluginMetadata(
  name="复读",
  description="基于一定规则重复群友的话",
  usage="""被动技能""",
  extra={"group": "娱乐", "commands": []},
)


class RepeaterState:
  def __init__(self):
    self.last_message: dict[str, Message] = {}
    self.message_times: dict[str, int] = {}
    self.shortest_times = 2
    self.ban_groups = get_plugin_config("repeater").get("ban_groups", [])
    self.whitelist_users = get_plugin_config("repeater").get("whitelist_users", [])


_state = RepeaterState()


def _is_group_message(event: GroupMessageEvent) -> bool:
  return True


repeater = on_message(rule=Rule(_is_group_message))


@repeater.handle()
async def repeater_handler(bot: Bot, event: GroupMessageEvent):
  raw_message = event.get_plaintext()
  message = event.get_message()

  if not bot.adapter.get_name() == "OneBot V11":
    return

  gid = str(event.group_id)
  uid = int(event.user_id)

  for addon in hm.Addons.values():
    for command in addon.commands:
      if command in raw_message:
        return

  if message != _state.last_message.get(gid):
    _state.message_times[gid] = 1
  else:
    _state.message_times[gid] += 1

  if _state.message_times.get(gid) == _state.shortest_times:
    await repeater.finish(message)
  elif _state.message_times.get(gid, 1) > _state.shortest_times and event.group_id in _state.ban_groups:
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
    random_num = random.randint(random_range[0], random_range[1])
    chosen_range_index = ranges.index(random_range)

    if uid in _state.whitelist_users:
      return

    botv11 = cast(BotV11, bot)
    if await is_admin(botv11, event):
      await repeater.finish("不就是管理员么, 有什么了不起的!")
    await bot.set_group_ban(group_id=event.group_id, user_id=event.user_id, duration=random_num * 60)
    username = event.sender.nickname
    await repeater.finish(f"恭喜{username}获得「{award[chosen_range_index]}级」禁言卡,将在{random_num}分钟后解禁")

  _state.last_message[gid] = message
