from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
  name="消息撤回",
  description="撤回指定的消息。",
  usage="使用方法: 撤回 [回复的消息]",
  extra={"group": "群管", "commands": ["撤回"]},
)

revoke = on_command("撤回")


@revoke.handle()
async def _rk(bot: Bot, event: GroupMessageEvent):
  if reply := event.reply:
    await bot.delete_msg(message_id=reply.message_id)
