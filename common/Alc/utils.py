import re

from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import Arparma, CommandMeta


def pm(name: str, description: str, usage: str, group: str):
  """生成nb插件元数据

  Args:
      name (str): 名称
      description (str): 描述
      usage (str): 用法
      group (str): 分组

  Returns:
      PluginMetadata: 插件元数据
  """
  extra = {"group": group}
  return PluginMetadata(name=name, description=description, usage=usage, extra=extra)


def ptc(p: PluginMetadata) -> CommandMeta:
  """nb插件元数据转alc指令元数据

  Args:
      p (PluginMetadata): nb插件元数据

  Returns:
      CommandMeta: alc指令元数据
  """
  c = CommandMeta()
  c.description = p.description
  c.usage = p.usage
  c.extra = p.extra
  c.extra.setdefault("name", p.name)
  c.extra.setdefault("group", p.extra.get("group", "未命名"))

  return c


def get_source_command(
  result: Arparma,
):
  """
  获取 alc context 匹配命令, 用于获取aliases
  """
  match_object = result.context.get("$shortcut.regex_match")

  if isinstance(match_object, re.Match):
    return match_object.group(0)

  return result.header_result
