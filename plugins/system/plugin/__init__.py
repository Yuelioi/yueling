from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.exception import IgnoredException
from nonebot.matcher import Matcher
from nonebot.message import run_preprocessor
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from core.deps import Args
from core.handler import register_handler
from core import store
from core.context import ToolContext
from core.permission import is_admin, is_superuser, permission_manager
from plugins.system.plugin.manager import hm

__plugin_meta__ = PluginMetadata(
  name="插件管理",
  description="禁用 / 启用 插件（需要管理员权限）",
  usage="""禁用/启用插件 [插件编号|插件名称]""",
  extra={
    "group": "系统",
    "commands": ["禁用插件", "启用插件", "查看禁用"],
    "tools": [{
      "name": "manage_plugin",
      "description": "在当前群禁用或启用指定插件（需要管理员权限）",
      "tags": ["moderation", "group"],
      "examples": ["禁用翻译插件", "启用OCR", "查看禁用了哪些插件"],
      "parameters": {
        "action": {"type": "string", "description": "操作: disable/enable/list"},
        "plugin_name": {"type": "string", "description": "插件名称（action=list时可不填）", "default": ""},
      },
      "permission": "admin",
      "handler": "plugin_tool_handler",
    }],
  },
)
manager = on_command("禁用插件", aliases={"启用插件", "查看禁用"})
user_block = on_command("屏蔽功能", aliases={"取消屏蔽", "我的屏蔽"})


@run_preprocessor
async def block_plugin(matcher: Matcher, event: GroupMessageEvent):
  plugin = matcher.plugin
  if not plugin or not plugin.metadata:
    return
  name = plugin.metadata.name
  ban = store.group_blacklist.get(event.group_id, [])
  if name in ban:
    raise IgnoredException("")
  if permission_manager.is_user_blocked(name, event.user_id):
    raise IgnoredException("")


async def manager_handler(bot: Bot, event: GroupMessageEvent, cmd=RawCommand(), args: list[str] = Args(0, 999)):
  if cmd != "查看禁用":
    if not is_superuser(event) and not await is_admin(bot, event):
      return "需要管理员权限"

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


# ─── AI Tool 入口 ─────────────────────────────────────────

async def plugin_tool_handler(ctx: ToolContext, action: str, plugin_name: str = "") -> str:
  if action == "list":
    ban = store.group_blacklist.get(ctx.group_id, [])
    if ban:
      return "已禁用: " + "、".join(ban)
    return "当前没有禁用任何插件"

  if not plugin_name:
    return "请指定插件名称"

  addon = hm.get_addon(plugin_name)
  if not addon:
    available = [a.name for a in hm.Addons.values() if not a.hidden]
    return f"未找到插件'{plugin_name}'，可用: {', '.join(available[:10])}"

  ban = store.group_blacklist.get(ctx.group_id, [])

  if action == "disable":
    if addon.name in ban:
      return f"{addon.name} 已经是禁用状态"
    ban.append(addon.name)
    store.group_blacklist[ctx.group_id] = ban
    store.group_blacklist.save()
    return f"已禁用 {addon.name}"

  elif action == "enable":
    if addon.name not in ban:
      return f"{addon.name} 没有被禁用"
    ban.remove(addon.name)
    store.group_blacklist[ctx.group_id] = ban
    store.group_blacklist.save()
    return f"已启用 {addon.name}"

  return "未知操作，请使用 disable/enable/list"


# ─── 用户个人屏蔽 ─────────────────────────────────────────


async def user_block_handler(event: GroupMessageEvent, cmd=RawCommand(), args: list[str] = Args(0, 999)):
  user_id = event.user_id

  if cmd == "我的屏蔽":
    blocked = permission_manager.get_user_blocked_plugins(user_id)
    if blocked:
      return "你屏蔽的功能: " + "、".join(blocked)
    return "你没有屏蔽任何功能"

  if not args:
    available = [a.name for a in hm.Addons.values() if not a.hidden]
    return f"请指定功能名称，可用: {', '.join(available[:15])}"

  results = []
  for arg in args:
    addon = hm.get_addon(arg)
    if not addon:
      results.append(f"未找到'{arg}'")
      continue
    if cmd == "屏蔽功能":
      permission_manager.block_user_plugin(addon.name, user_id)
      results.append(f"已屏蔽 {addon.name}")
    else:
      permission_manager.unblock_user_plugin(addon.name, user_id)
      results.append(f"已取消屏蔽 {addon.name}")

  return "\n".join(results)


register_handler(user_block, user_block_handler)
