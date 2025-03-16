from nonebot import get_driver, logger, on_command, on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from common.base.Handle import register_handler
from common.database.ReplyManager import Reply, rpm

reply_data = {}
driver = get_driver()


@driver.on_bot_connect
async def _():
  logger.opt(colors=True).success('<yellow>更新回复字典成功</yellow> from <magenta>nonebot_plugin_yuelibot.plugins.reply</magenta>"')
  update_reply()


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
    return res.replace("回复7:", "")


register_handler(reply, handle_reply)


def reply_modify_handle(event: GroupMessageEvent, args: list[str], cmd=RawCommand()):
  if cmd == "添加回复":
    content = " ".join(args[1:])
    content = content.replace("\\n", "\n")
    rep = Reply(qq=event.user_id, keyword=args[0], reply=content, group=None)
    if rpm.insert_data(rep):
      update_reply()
      return "添加成功"
    return "添加失败了喵~"
  elif "删除回复" == cmd:
    if rpm.delete_reply_data(int(args[0])):
      update_reply()
      return "删除成功"
    return "删除失败"
  else:
    update_reply()


def update_reply():
  global reply_data
  reply_data.clear()
  if sqldata := rpm.get_reply_data():
    for data in sqldata:
      keys = data["keyword"].split(",")
      suffix = f"{data['group']}" if data["group"] else ""
      for key in keys:
        reply = data["reply"].replace("{}", key) if "{}" in data["reply"] else data["reply"]
        reply_data[(key + suffix).lower()] = f"回复{data['id']}:{reply} "


register_handler(reply_modify, reply_modify_handle)
