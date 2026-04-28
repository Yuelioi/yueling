"""好感度查询命令（聊天功能已融入 AI 调度）"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata

from core.handler import register_handler
from core import store
from core.context import ToolContext
from ai.relation import get_relationship_info

__plugin_meta__ = PluginMetadata(
  name="好感度",
  description="查看与月灵的好感度",
  usage="""查看好感度""",
  extra={
    "group": "娱乐",
    "commands": ["查看好感度"],
    "tools": [{
      "name": "check_affinity",
      "description": "查看用户与月灵的好感度和关系状态",
      "tags": ["context"],
      "examples": ["我们关系怎么样", "你喜欢我吗", "好感度多少"],
      "parameters": {
        "user": {"type": "integer", "description": "QQ号，0=当前用户", "default": 0},
      },
      "handler": "affinity_tool_handler",
    }],
  },
)

pref_cmd = on_command("查看好感度", aliases={"查询好感度"})


async def pref_handler(event: GroupMessageEvent):
  user_id = str(event.user_id)
  user_like = store.user_prefs.get(user_id, 50)
  info = get_relationship_info(user_like)
  return f"好感度: {user_like}/100\n关系: {info['relationship']}\n态度: {info['attitude']}"


register_handler(pref_cmd, pref_handler)


async def affinity_tool_handler(ctx: ToolContext, user: int = 0) -> str:
  target = user or ctx.user_id
  user_like = store.user_prefs.get(str(target), 50)
  info = get_relationship_info(user_like)
  return f"好感度: {user_like}/100 | 关系: {info['relationship']} | 态度: {info['attitude']}"
