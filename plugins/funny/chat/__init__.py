from nonebot import on_command, on_message
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from common.base.Depends import Args, At
from common.base.Handle import register_handler
from common.config import gv
from plugins.funny.chat.utils import chat_ai

from .relation import get_relationship_info

__plugin_meta__ = PluginMetadata(
  name="聊天功能",
  description="提供基础聊天功能",
  usage="""月灵 + 内容""",
  extra={
    "group": "娱乐",
    "commands": ["chat", "添加喜好", "查看喜好", "删除喜好"],
  },
)

# url = f"https://api.yujn.cn/api/moli.php?msg={arg}"

matcher = on_message()


@matcher.handle()
async def chat_handle(bot: Bot, event: GroupMessageEvent, at=At()):
  msg = event.get_plaintext()

  if (at and str(at) == bot.self_id) or msg.startswith("chat"):
    msg = event.get_plaintext()
    MSG = msg.replace("chat", "").strip()
    user_id = event.user_id
    user_info = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=user_id, no_cache=True)
    group_messages = await bot.call_api("get_group_msg_history", group_id=event.group_id, message_id=str(event.message_id), count=40)
    msgs = []
    if group_messages:
      msg = group_messages["messages"]
    msg = chat_ai(MSG, user_info, msgs)
    await matcher.finish(msg)


user_pref_cmd = on_command("查看好感度", aliases={"查询好感度"})


async def pref(bot: Bot, event: GroupMessageEvent, args: list[str] = Args(0), cmd=RawCommand()):
  user_id = str(event.user_id)

  # if cmd == "查看好感度":
  # 添加喜好

  user_like = gv.user_prefs.get(user_id, 50)
  info = get_relationship_info(user_like)
  return f"""好感度:{user_like} 关系:{info["relationship"]}"""
  # else:
  #   # 取消喜好
  #   user_prefs = gv.user_prefs

  #   top3_ids = [user_id for user_id, _ in sorted(user_prefs.items(), key=lambda x: x[1], reverse=True)[:3]]
  #   if not top3_ids:
  #     return "当前无人在榜"

  #   user_info = await bot.call_api("get_group_member_info", group_id=event.group_id, user_id=user_id, no_cache=True)

  #   if not all(arg not in user_prefs for arg in args):
  #     user_prefs[:] = [arg for arg in user_prefs if arg not in args]
  #     gv.user_prefs.save()

  #   return "删除喜好蔽成功!"


register_handler(user_pref_cmd, pref)
