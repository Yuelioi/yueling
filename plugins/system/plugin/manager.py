from functools import cached_property
from typing import Callable  # noqa

from nonebot.plugin import get_loaded_plugins
from pydantic import BaseModel


class Addon(BaseModel):
  id: int
  name: str
  description: str
  usage: str
  group: str
  hidden: bool = False
  help_msg: Callable | None = None
  commands: list[str]

  def help(self):
    return f"""分组: {self.group}
名称: {self.name}
描述: {self.description}
用法: {self.usage}
"""


class HelpManager(BaseModel):
  groups: set[str] = set()

  # 所有指令
  @cached_property
  def Addons(self):
    plugins = get_loaded_plugins()

    _addons: dict[str, Addon] = {}
    for i, plugin in enumerate(plugins):
      meta = plugin.metadata
      if not meta:
        continue

      extra = meta.extra
      name = meta.name
      group = extra.get("group", "三方插件")
      usage = meta.usage or "未设置用法"
      hidden = extra.get("hidden", False)
      self.groups.add(group)

      if group == "三方插件":
        if not name.startswith("nonebot"):
          continue
      _addons.setdefault(
        name,
        Addon(id=i + 1, name=name, description=meta.description, usage=usage, group=group, hidden=hidden, commands=extra.get("commands", [])),
      )
    return _addons

  def search(self, name: str):
    try:
      if addon := self.get_addon(name):
        return addon.help()

      if name in self.groups:
        if doc := self.by_group(name):
          return doc

      return "未找到该插件"
    except Exception as e:
      return f"搜索命令时发生错误{e}"

  def get_addon(self, name: str):
    if name.isdigit():
      return self.get_addon_by_id(int(name))
    return self.get_addon_by_name(name)

  def get_addon_by_name(self, name: str):
    return self.Addons.get(name)

  def get_addon_by_id(self, i: int):
    for addon in self.Addons.values():
      if addon.id == i:
        return addon

  def by_group(self, name: str):
    res = [f"ID:{addon.id} 名称:{addon.name}" for addon in self.Addons.values() if addon.group == name]
    if not res:
      return
    return f"---{name}---\nhelp + ID/名称 查看具体用法\n" + "\n".join(res)

  def all_help(self):
    """
    所有命令的帮助信息 不包括隐藏命令
    """
    grouped_Addons = {}

    for addon in self.Addons.values():
      if addon.hidden:
        continue
      if addon.group not in grouped_Addons:
        grouped_Addons[addon.group] = []
      grouped_Addons[addon.group].append(f"ID:{addon.id} 名称:{addon.name}")

    help_messages = ["使用help + ID/名称查看详细帮助"]
    for group, Addons in grouped_Addons.items():
      help_messages.append(f"---{group}---")
      help_messages.extend(Addons)
    return help_messages


hm = HelpManager()
