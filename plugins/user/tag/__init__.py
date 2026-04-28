import json
import re

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from core.deps import Args
from core.handler import register_handler
from core.config import config
from core.context import ToolContext
from core import store

__plugin_meta__ = PluginMetadata(
  name="用户标签",
  description="管理个人标签",
  usage="""我的标签/添加标签/删除标签""",
  extra={
    "group": "用户",
    "commands": ["我的标签", "添加标签", "删除标签"],
    "tools": [{
      "name": "get_user_tags",
      "description": "查看用户的个人标签",
      "tags": ["context"],
      "examples": ["他的标签是什么", "这个人有什么标签"],
      "parameters": {
        "user": {"type": "integer", "description": "QQ号，0=当前用户", "default": 0},
      },
      "handler": "tags_tool_handler",
    }],
  },
)

tags = on_command("我的标签", aliases={"添加标签", "删除标签"})


tag_file = config.paths.database / "user_tag.json"


def split_tags(text: str) -> list:
  # 处理空字符串和纯空格情况
  if not text.strip():
    return []

  # 分割并过滤空标签
  return [tag.strip() for tag in re.split(r"\s*,\s*", text.replace("，", ",")) if tag.strip()]


def save_tags(data: dict):
  """保存标签数据"""
  with tag_file.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


async def tag_handle(event: GroupMessageEvent, cmd: str = RawCommand(), args_list: list[str] = Args(0, 999)):
  user_id = str(event.user_id)

  # 加载现有数据
  current_tags = store.user_tags.get(user_id, [])

  if cmd == "我的标签":
    if not current_tags:
      return "您还没有任何标签哦~"
    return "当前标签为：\n" + ",".join(current_tags)

  elif cmd == "添加标签":
    if len(current_tags) >= 3:
      return "最多支持3个标签喔~"
    text = " ".join(args_list)
    new_tags = split_tags(text)
    if not new_tags:
      return "请提供要添加的标签内容"

    current_tags.extend(new_tags)
    filtered_tags = list(set(current_tags))
    store.user_tags[user_id] = filtered_tags[:3]
    store.user_tags.save()

    return "添加成功!"

  elif cmd == "删除标签":
    if not args_list:
      return "请提供要删除的标签内容"

    text = " ".join(args_list)
    new_tags = split_tags(text)

    for tag in new_tags:
      if tag in current_tags:
        current_tags.remove(tag)

    store.user_tags[user_id] = current_tags
    store.user_tags.save()

    if not current_tags:
      return "删除成功, 当前无任何标签"
    return "删除成功!"

  return "无效的命令参数"


register_handler(tags, tag_handle)


async def tags_tool_handler(ctx: ToolContext, user: int = 0) -> str:
  target = str(user or ctx.user_id)
  current_tags = store.user_tags.get(target, [])
  if not current_tags:
    return "该用户没有标签"
  return "用户标签: " + ", ".join(current_tags)
