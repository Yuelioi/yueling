import time

from nonebot import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule

from core.config import config, get_plugin_config

__plugin_meta__ = PluginMetadata(
  name="recorder",
  description="特定群友欢迎图",
  usage="定时发送",
  extra={"group": "娱乐", "hidden": True, "commands": []},
)


class _State:
  last_trigger_time: float = 0


_state = _State()


def _in_target_group(event: GroupMessageEvent) -> bool:
  return event.group_id in get_plugin_config("recorder").get("target_groups", [])


recorder = on_message(rule=Rule(_in_target_group))


@recorder.handle()
async def recorder_handler(event: GroupMessageEvent):
  special_users = get_plugin_config("recorder").get("special_users", {})
  user_key = str(event.user_id)
  if user_key in special_users:
    now = time.time()
    if now - _state.last_trigger_time > 3600:
      img = config.paths.images / special_users[user_key]
      _state.last_trigger_time = now
      await recorder.finish(MessageSegment.image(img))
