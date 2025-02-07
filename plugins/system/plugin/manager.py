from dataclasses import MISSING, fields
from functools import cached_property
from typing import Callable  # noqa

from nonebot_plugin_alconna import CommandMeta, command_manager
from pydantic import BaseModel


class Command(BaseModel):
  id: int
  name: str
  description: str
  usage: str
  group: str
  hidden: bool = False
  help_msg: Callable | None = None

  def help(self):
    return f"""分组: {self.group}
名称: {self.name}
描述: {self.description}
用法: {self.usage}
"""


class HelpManager(BaseModel):
  groups: set[str] = set()

  @cached_property
  def commands(self):
    try:
      cmds = command_manager.get_commands()
    except Exception:
      return {}
    _commands: dict[str, Command] = {}
    for i, cmd in enumerate(cmds):
      if is_default_command_meta(cmd.meta):
        continue
      extra = cmd.meta.extra
      name = extra.get("name", "未命名")
      group = extra.get("group", "未命名")
      usage = cmd.meta.usage or "未设置用法"
      hidden = extra.get("hidden", False)
      self.groups.add(group)
      _commands.setdefault(
        name,
        Command(
          id=i + 1,
          name=name,
          description=cmd.meta.description,
          usage=usage,
          group=group,
          hidden=hidden,
        ),
      )
    return _commands

  def search(self, name: str):
    try:
      if cmd := self.get_cmd(name):
        return cmd.help()

      if name in self.groups:
        if doc := self.by_group(name):
          return doc

      return "未找到该插件"
    except Exception as e:
      return f"搜索命令时发生错误{e}"

  def get_cmd(self, name: str):
    if name.isdigit():
      return self.get_cmd_by_id(int(name))
    return self.get_cmd_by_name(name)

  def get_cmd_by_name(self, name: str):
    return self.commands.get(name)

  def get_cmd_by_id(self, i: int):
    for cmd in self.commands.values():
      if cmd.id == i:
        return cmd

  def by_group(self, name: str):
    res = [f"ID:{cmd.id} 名称:{cmd.name}" for cmd in self.commands.values() if cmd.group == name]
    if not res:
      return
    return f"---{name}---\nhelp + ID/名称 查看具体用法\n" + "\n".join(res)

  def all_help(self):
    """
    所有命令的帮助信息 不包括隐藏命令
    """
    grouped_commands = {}

    for cmd in self.commands.values():
      if cmd.hidden:
        continue
      if cmd.group not in grouped_commands:
        grouped_commands[cmd.group] = []
      grouped_commands[cmd.group].append(f"ID:{cmd.id} 名称:{cmd.name}")

    help_messages = ["使用help + ID/名称查看详细帮助"]
    for group, commands in grouped_commands.items():
      help_messages.append(f"---{group}---")
      help_messages.extend(commands)
    return help_messages


def is_default_command_meta(instance: CommandMeta) -> bool:
  """
  判断一个命令元信息是否是默认的命令元信息
  """
  for field in fields(instance):
    instance_value = getattr(instance, field.name)

    if field.name == "extra":
      continue

    if field.default is not MISSING and field.default != instance_value:
      return False

    if field.default_factory is not MISSING:
      if field.default_factory is dict:
        default_value = {}
      else:
        default_value = field.default_factory()

      if default_value != instance_value:
        return False

  return True


hm = HelpManager()
