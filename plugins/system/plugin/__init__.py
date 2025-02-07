import json

import aiofiles
from nonebot.adapters import Bot
from nonebot.exception import IgnoredException
from nonebot.message import run_preprocessor
from nonebot_plugin_alconna import AlconnaMatcher, Arparma, MsgTarget, on_alconna

from common.Alc.Alc import args, pm, ptc
from common.Alc.Permission import User_Checker
from common.config import config, gv
from plugins.system.plugin.manager import hm

__plugin_meta__ = pm(
  name="插件管理",
  description="禁用 / 启用 插件",
  usage="""禁用/启用插件 [插件编号|插件名称]""",
  group="系统",
)
_manage = args("禁用插件", required=False, meta=ptc(__plugin_meta__))
manage = on_alconna(_manage, aliases={"启用插件", "查看禁用"})


@run_preprocessor
async def do_something(target: MsgTarget, matcher: AlconnaMatcher):
  if target.private:
    return

  cmd = matcher.command()

  if ban := gv.group_black_list.get(target.id, []):
    if cmd.meta.extra.get("name") in ban:
      raise IgnoredException("")


@manage.assign("$main", additional=User_Checker)
async def mana(target: MsgTarget, result: Arparma, args: list[str] = []):
  if target.private:
    return

  if "查看禁用" in result.header_match.origin:
    cmd = "查看禁用"
  elif "禁用" in result.header_match.origin:
    cmd = "禁用插件"
  else:
    cmd = "启用插件"

  # 查看禁用
  if cmd == "查看禁用":
    if ban := gv.group_black_list.get(target.id, []):
      msg = "已禁用的插件为" + " ".join(map(str, ban))
    else:
      msg = "当前没有禁用任何插件"
    await manage.finish(msg)

  if not args:
    await manage.finish("请输入插件名称或编号")
  # 获取有效插件列表
  plugins: list[str] = []
  for arg in args:
    plugin = hm.get_cmd(arg)
    if not plugin:
      continue
    plugins.append(plugin.name)
  if not plugins:
    await manage.finish("未找到相关插件")

  msg = "已启用:" if cmd == "启用插件" else "已禁用:"
  # 修改禁用列表
  ban = gv.group_black_list.get(target.id, [])

  for plugin in plugins:
    if plugin in ban:
      if cmd == "启用插件":
        ban.remove(plugin)
      else:
        continue
    else:
      if cmd != "启用插件":
        ban.append(plugin)

    msg += plugin + " "

  gv.group_black_list[target.id] = ban

  async with aiofiles.open(config.data.group_black_list, "w") as f:
    await f.write(json.dumps(gv.group_black_list, ensure_ascii=False, indent=4))

  # 返回结果
  await manage.finish(msg)
