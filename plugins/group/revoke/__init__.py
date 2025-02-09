from nonebot.adapters.onebot.v11 import Bot
from nonebot_plugin_alconna import Alconna, MsgId, on_alconna
from nonebot_plugin_alconna.builtins.extensions import ReplyRecordExtension

from common.Alc.Alc import pm, ptc

__plugin_meta__ = pm(
  name="消息撤回",
  description="撤回指定的消息。",
  usage="使用方法: 撤回 [回复的消息]",
  group="群管",
)

_revoke = Alconna("撤回", meta=ptc(__plugin_meta__))
revoke = on_alconna(_revoke, extensions=[ReplyRecordExtension])


@revoke.handle()
async def _rk(bot: Bot, msg_id: MsgId, ext: ReplyRecordExtension):
  if reply := ext.get_reply(msg_id):
    await bot.delete_msg(message_id=int(reply.id))
