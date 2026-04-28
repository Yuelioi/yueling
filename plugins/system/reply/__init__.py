from nonebot import get_driver, logger, on_command, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from core.deps import Args
from core.handler import register_handler
from repositories.reply_repo import reply_repo

reply_data = {}
driver = get_driver()


@driver.on_bot_connect
async def _():
  await update_reply()
  logger.info("回复字典加载完成")


__plugin_meta__ = PluginMetadata(
  name="应答系统",
  description="基于关键词回复设定内容",
  usage="""添加回复/删除回复/更新回复""",
  extra={
    "group": "系统",
  },
)

reply = on_message()

reply_modify = on_command("添加回复", aliases={"删除回复", "更新回复"})


async def handle_reply(event: GroupMessageEvent):
  msg = str(event.get_plaintext()).lower()
  if res := reply_data.get(msg):
    return res


register_handler(reply, handle_reply)


async def reply_modify_handle(event: GroupMessageEvent, args: list[str] = Args(), cmd=RawCommand()):
  if cmd == "添加回复":
    content = " ".join(args[1:])
    content = content.replace("\\n", "\n")
    if await reply_repo.add(qq=event.user_id, keyword=args[0], reply=content):
      await update_reply()
      return "添加成功"
    return "添加失败了喵~"
  elif "删除回复" == cmd:
    if await reply_repo.delete_by_id(int(args[0])):
      await update_reply()
      return "删除成功"
    return "删除失败"
  else:
    await update_reply()


async def update_reply():
  global reply_data
  reply_data.clear()
  all_replies = await reply_repo.get_all()
  for data in all_replies:
    if not data.keyword:
      continue
    keys = data.keyword.split(",")
    suffix = data.group or ""
    for key in keys:
      reply_text = data.reply or ""
      reply_text = reply_text.replace("{}", key) if "{}" in reply_text else reply_text
      reply_data[(key + suffix).lower()] = reply_text


register_handler(reply_modify, reply_modify_handle)
