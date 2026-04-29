"""好感度查询命令（聊天功能已融入 AI 调度）"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata

from core.handler import register_handler
from core import store
from ai.relation import get_relationship_info

__plugin_meta__ = PluginMetadata(
  name="好感度",
  description="查看与月灵的好感度",
  usage="""查看好感度""",
  extra={
    "group": "娱乐",
    "commands": ["查看好感度"],
  },
)

pref_cmd = on_command("查看好感度", aliases={"查询好感度"})


async def pref_handler(event: GroupMessageEvent):
  user_id = str(event.user_id)
  user_like = store.user_prefs.get(user_id, 50)
  info = get_relationship_info(user_like)
  return f"好感度: {user_like}/100\n关系: {info['relationship']}\n态度: {info['attitude']}"


register_handler(pref_cmd, pref_handler)
