from nonebot import on_request
from nonebot.adapters.onebot.v11 import Bot, GroupRequestEvent
from nonebot.plugin import PluginMetadata

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

  if event.group_id == 587443081:
    if "月离" in comment or "b" in comment or "哔" in comment:
      await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=True, reason=" ")

  elif event.group_id == 885816198:
    if comment == "java":
      await bot.bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=False, reason="答案错误")
    if ("j" in comment and "s" in comment) or ("e" in comment and "s" in comment):
      await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=True, reason=" ")

  elif event.group_id == 680653092:
    if "video" in comment:
      await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=True, reason=" ")
  elif event.group_id == 151998078:
    if comment != "":
      await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=True, reason=" ")

  if "交流" in comment or "我是" in comment:
    await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=False, reason="机器人爬")
