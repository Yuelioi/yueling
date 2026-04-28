from nonebot import on_request
from nonebot.adapters.onebot.v11 import Bot, GroupRequestEvent
from nonebot.plugin import PluginMetadata

from core.config import get_plugin_config

gr = on_request()


__plugin_meta__ = PluginMetadata(
  name="入群验证",
  description="自动入群",
  usage="基于关键词,自动允许加群",
  extra={"group": "群管"},
)


@gr.handle()
async def _(bot: Bot, event: GroupRequestEvent):
  comment = event.comment
  if not comment:
    return

  comment = comment.lower()

  auto_approve = get_plugin_config("manager").get("auto_approve", {})
  group_key = str(event.group_id)

  if group_key in auto_approve:
    keywords = auto_approve[group_key]
    if keywords == ["*"]:
      if comment:
        await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=True, reason=" ")
        return
    elif any(kw in comment for kw in keywords):
      await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=True, reason=" ")
      return

  if "交流" in comment or "我是" in comment:
    await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=False, reason="机器人爬")
