from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.exception import IgnoredException
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from core.deps import Args
from core.handler import register_handler
from core import store
from plugins.system.plugin.manager import hm

__plugin_meta__ = PluginMetadata(
  name="插件管理",
  description="禁用 / 启用 插件",
  usage="""禁用/启用插件 [插件编号|插件名称]""",
  extra={"group": "系统", "comands": ["禁用插件", "启用插件", "查看禁用"]},
)
manager = on_command("禁用插件", aliases={"启用插件", "查看禁用"})


@run_preprocessor
async def block_plugin(matcher: Matcher, event: GroupMessageEvent):
  ban = store.group_blacklist.get(event.group_id, [])
  if (plugin := matcher.plugin) and (meta := plugin.metadata) and meta.name in ban:
    raise IgnoredException("")


async def manager_handler(event: GroupMessageEvent, cmd=RawCommand(), args: list[str] = Args(0, 999)):
  # 查看禁用
  if cmd == "查看禁用":
    if ban := store.group_blacklist.get(event.group_id, []):
      return "已禁用的插件为" + " ".join(map(str, ban))
    else:
      return "当前没有禁用任何插件"

  if not args:
    return "请输入插件名称或编号"

  # 获取有效插件列表
  addons: list[str] = []
  for arg in args:
    addon = hm.get_addon(arg)
    if not addon:
      continue
    addons.append(addon.name)
  if not addons:
    return "未找到相关插件"

  msg = "已启用:" if cmd == "启用插件" else "已禁用:"
  # 修改禁用列表
  ban = store.group_blacklist.get(event.group_id, [])

  for addon in addons:
    if addon in ban:
      if cmd == "启用插件":
        ban.remove(addon)
      else:
        continue
    else:
      if cmd != "启用插件":
        ban.append(addon)

    msg += addon + " "

  store.group_blacklist[event.group_id] = ban
  store.group_blacklist.save()

  # 返回结果
  return msg


register_handler(manager, manager_handler)
