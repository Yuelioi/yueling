import json

import aiofiles
from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.exception import IgnoredException
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from common.base.Depends import Args
from common.config import config, gv
from plugins.system.plugin.manager import hm

__plugin_meta__ = PluginMetadata(
  name="插件管理",
  description="禁用 / 启用 插件",
  usage="""禁用/启用插件 [插件编号|插件名称]""",
  extra={"group": "系统", "comands": ["禁用插件", "启用插件", "查看禁用"]},
)
manage = on_command("禁用插件", aliases={"启用插件", "查看禁用"})


@run_preprocessor
async def do_something(matcher: Matcher, event: GroupMessageEvent):
  plugin = matcher.plugin_name

  if ban := gv.group_black_list.get(event.group_id, []):
    if plugin in ban:
      raise IgnoredException("")


@manage.handle()
async def mana(event: GroupMessageEvent, cmd=RawCommand(), args: list[str] = Args()):
  # 查看禁用
  if cmd == "查看禁用":
    if ban := gv.group_black_list.get(event.group_id, []):
      msg = "已禁用的插件为" + " ".join(map(str, ban))
    else:
      msg = "当前没有禁用任何插件"
    await manage.finish(msg)

  if not args:
    await manage.finish("请输入插件名称或编号")

  # 获取有效插件列表
  addons: list[str] = []
  for arg in args:
    addon = hm.get_addon(arg)
    if not addon:
      continue
    addons.append(addon.name)
  if not addons:
    await manage.finish("未找到相关插件")

  msg = "已启用:" if cmd == "启用插件" else "已禁用:"
  # 修改禁用列表
  ban = gv.group_black_list.get(event.group_id, [])

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

  gv.group_black_list[event.group_id] = ban

  async with aiofiles.open(config.data.group_black_list, "w") as f:
    await f.write(json.dumps(gv.group_black_list, ensure_ascii=False, indent=4))

  # 返回结果
  await manage.finish(msg)
