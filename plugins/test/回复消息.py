from nonebot_plugin_alconna import AlcMatches, Alconna, Image, MsgId, UniMsg, on_alconna
from nonebot_plugin_alconna.builtins.extensions import ReplyRecordExtension
from nonebot_plugin_alconna.builtins.extensions.reply import ReplyMergeExtension

bind = on_alconna(Alconna("bind"), extensions=[ReplyRecordExtension()])
bind2 = on_alconna(Alconna("bind2"), extensions=[ReplyMergeExtension()])


# 获取消息ID以及所在的回复消息
@bind.handle()
async def bind_handle(msg_id: MsgId, ext: ReplyRecordExtension):
  """
  @param msg_id: 消息ID
  @param ext: ReplyRecordExtension
  reply_id = ext.get_reply(msg_id).id
  """
  reply = ext.get_reply(msg_id)


# 拿到回复里的图片
@bind2.handle()
async def bind2_handle(msg: UniMsg, am: AlcMatches):
  print(am)
  if msg.has(Image):
    imgs = msg.get(Image)
    for img in imgs:
      print(img.url)
