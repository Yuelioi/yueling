from nonebot import on_request
from nonebot.adapters.onebot.v11 import Bot, GroupRequestEvent

gr = on_request()


@gr.handle()
async def _(bot: Bot, event: GroupRequestEvent):
  comment = event.comment
  if not comment:
    return

  comment = comment.lower()
  if event.group_id == 587443081:
    if "月离" in comment or "bili" in comment or "哔" in comment:
      await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=True, reason=" ")

  elif event.group_id == 885816198:
    if "j" in comment and "s" in comment:
      await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=True, reason=" ")

  elif event.group_id == 680653092:
    if "video" in comment:
      await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=True, reason=" ")
  elif event.group_id == 151998078:
    if comment != "":
      await bot.set_group_add_request(flag=event.flag, sub_type=event.sub_type, approve=True, reason=" ")
