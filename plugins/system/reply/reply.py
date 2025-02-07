# from nonebot import get_driver, logger
# from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
# from nonebot.params import EventPlainText, RawCommand

# from common.base import Arg, Args
# # from common.base.ReplyManager import Reply, rpm

# reply_data = {}
# driver = get_driver()


# @driver.on_bot_connect
# async def _():
#   logger.opt(colors=True).success(
#     '<yellow>更新回复字典成功</yellow> from <magenta>nonebot_plugin_yuelibot.plugins.reply</magenta>"'
#   )
#   update_reply()


# async def handle_reply(event: GroupMessageEvent, msg=EventPlainText()):
#   msg = msg.strip().lower()
#   if res := reply_data.get(f"{msg}{event.group_id!s}") or reply_data.get(msg):
#     return MessageSegment.text(res.replace("回复7:", ""))


# def add_reply(event: GroupMessageEvent, args=Args(2, 100), cmd=RawCommand()):
#   group = ""
#   if cmd == "添加本群回复":
#     group = str(event.group_id)
#   rep = Reply(qq=event.user_id, keyword=args[0], reply=" ".join(args[1:]), group=group)
#   if rpm.insert_data(rep):
#     update_reply()
#     return "添加成功"
#   return "添加失败了喵~"


# def update_reply():
#   global reply_data
#   reply_data.clear()
#   if sqldata := rpm.get_reply_data():
#     for data in sqldata:
#       keys = data["keyword"].split(",")
#       suffix = f"{data['group']}" if data["group"] else ""
#       for key in keys:
#         reply = data["reply"].replace("{}", key) if "{}" in data["reply"] else data["reply"]
#         reply_data[(key + suffix).lower()] = f"回复{data['id']}:{reply} "


# # 参数是回复ID
# def delete_reply(arg=Arg()):
#   if rpm.delete_reply_data(arg):
#     update_reply()
#     return "删除成功"

#   return "删除失败"
