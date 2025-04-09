from nonebot import on_command, on_message
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from common.base.Depends import Args, At
from common.base.Handle import register_handler
from common.config import gv
from plugins.funny.chat.utils import chat_ai

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
    group_messages = await bot.call_api("get_group_msg_history", group_id=event.group_id, message_id=str(event.message_id), count=100)

    msg = chat_ai(MSG, user_info, group_messages["messages"])
    await matcher.finish(msg)


user_pref_cmd = on_command("添加喜好", aliases={"删除喜好", "查看喜好"})


async def pref(event: GroupMessageEvent, args: list[str] = Args(0), cmd=RawCommand()):
  user_id = str(event.user_id)
  if cmd in ["添加喜好", "删除喜好"]:
    if not args:
      return "请指定关键词"

    if cmd == "添加喜好":
      # 添加喜好
      user_prefs = gv.user_prefs.setdefault(user_id, [])
      if not all(arg in user_prefs for arg in args):
        user_prefs.extend(arg for arg in args if arg not in user_prefs)
        gv.user_prefs.save()
      return "添加喜好成功!"

    else:
      # 取消喜好
      user_prefs = gv.user_prefs.get(user_id, [])
      if not all(arg not in user_prefs for arg in args):
        user_prefs[:] = [arg for arg in user_prefs if arg not in args]
        gv.user_prefs.save()

      return "删除喜好蔽成功!"

  # 查看喜好
  user_prefs = gv.user_prefs.get(str(event.user_id), [])
  if user_prefs:
    return "当前喜好词为: " + ", ".join(user_prefs)
  return "当前没有该喜好词"


register_handler(user_pref_cmd, pref)
