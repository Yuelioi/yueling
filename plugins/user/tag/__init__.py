import json
import re

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.params import RawCommand

from common.base.Depends import Args
from common.base.Handle import register_handler
from common.config import config

tags = on_command("我的标签", aliases={"添加标签", "删除标签"})


tag_file = config.resource.database / "user_tag.json"


def split_tags(text: str) -> list:
  # 处理空字符串和纯空格情况
  if not text.strip():
    return []

  # 分割并过滤空标签
  return [tag.strip() for tag in re.split(r"\s*,\s*", text.replace("，", ",")) if tag.strip()]


def load_tags() -> dict:
  """加载标签数据"""
  try:
    if tag_file.exists():
      with tag_file.open("r", encoding="utf-8") as f:
        return json.load(f)
    return {}
  except json.JSONDecodeError:
    return {}


config.user.tags = load_tags()


def save_tags(data: dict):
  """保存标签数据"""
  with tag_file.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)


async def tag_handle(event: GroupMessageEvent, cmd: str = RawCommand(), args_list: list[str] = Args(0, 999)):
  user_id = str(event.user_id)

  # 加载现有数据
  user_tags = config.user.tags.get(user_id, [])

  if cmd == "我的标签":
    if not user_tags:
      return "您还没有任何标签哦~"
    return f"当前标签为：\n" + ",".join(user_tags)

  elif cmd == "添加标签":
    if len(config.user.tags.get(user_id, [])) >= 3:
      return "最多支持3个标签喔~"
    text = " ".join(args_list)
    new_tags = split_tags(text)
    if not new_tags:
      return "请提供要添加的标签内容"

    user_tags.extend(new_tags)
    filtered_tags = list(set(user_tags))
    config.user.tags[user_id] = filtered_tags[:3]
    save_tags(config.user.tags)
    return f"添加成功, 当前标签为:\n{','.join(filtered_tags)}"

  elif cmd == "删除标签":
    if not args_list:
      return "请提供要删除的标签内容"

    text = " ".join(args_list)
    new_tags = split_tags(text)

    for tag in new_tags:
      if tag in user_tags:
        user_tags.remove(tag)
    config.user.tags[user_id] = user_tags
    save_tags(config.user.tags)

    if not user_tags:
      return "删除成功, 当前无任何标签"
    return f"删除成功, 当前标签为：\n{','.join(user_tags)}"

  return "无效的命令参数"


register_handler(tags, tag_handle)
