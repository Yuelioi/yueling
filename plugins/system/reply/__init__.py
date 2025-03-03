from nonebot import get_driver, logger
from nonebot_plugin_alconna import Arparma, MsgTarget, on_alconna

from common.Alc.Alc import args, msg, pm, ptc, register_handler
from common.database.ReplyManager import Reply, rpm

reply_data = {}
driver = get_driver()


@driver.on_bot_connect
async def _():
  logger.opt(colors=True).success('<yellow>更新回复字典成功</yellow> from <magenta>nonebot_plugin_yuelibot.plugins.reply</magenta>"')
  update_reply()


__plugin_meta__ = pm(
  name="应答系统",
  description="基于关键词回复设定内容",
  usage="""添加回复/删除回复/更新回复""",
  group="系统",
)
_reply = msg()

_reply.meta = ptc(__plugin_meta__)
reply = on_alconna(_reply)

_reply_modify = args("添加回复")
reply_modify = on_alconna(_reply_modify, aliases={"删除回复", "更新回复"})


async def handle_reply(result: Arparma):
  msg = str(result.origin).lower()
  if res := reply_data.get(msg):
    return res.replace("回复7:", "")


register_handler(reply, handle_reply)


def reply_modify_handle(result: Arparma, target: MsgTarget, args: list[str]):
  if "添加回复" in result.header_match.origin:
    content = " ".join(args[1:])
    content = content.replace("\\n", "\n")
    rep = Reply(qq=int(target.id), keyword=args[0], reply=content, group=None)
    if rpm.insert_data(rep):
      update_reply()
      return "添加成功"
    return "添加失败了喵~"
  elif "删除回复" in result.header_match.origin:
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
