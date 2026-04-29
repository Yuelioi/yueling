"""禁言 — 核心函数 + 双入口（支持 @、QQ号、昵称）"""

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata

from core.deps import Args, Ats
from core.config import config

__plugin_meta__ = PluginMetadata(
  name="禁言",
  description="禁言群友, 需要管理权限",
  usage="""禁言 + @群友/QQ号/昵称 [分钟数]""",
  extra={
    "group": "群管",
    "commands": ["禁言"],
  },
)


# ─── 核心函数 ─────────────────────────────────────────────


async def do_ban(bot: Bot, group_id: int, user_id: int, duration: int = 1) -> str:
  """执行禁言"""
  if duration < 1 or duration > 43200:
    return "禁言时长需要在1分钟到30天之间"

  members = await bot.get_group_member_list(group_id=group_id)
  if user_id not in {m["user_id"] for m in members}:
    return "目标用户不在群内"

  target_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
  if target_info.get("role") in ("admin", "owner"):
    return "管理何必为难管理"

  await bot.set_group_ban(group_id=group_id, user_id=user_id, duration=duration * 60)
  return f"已禁言 {duration} 分钟"


async def resolve_target(bot: Bot, group_id: int, event: GroupMessageEvent, target_str: str) -> int | None:
  """从 @、QQ号、昵称/群名片 解析目标用户"""
  for seg in event.message:
    if seg.type == "at" and str(seg.data.get("qq", "")) != str(bot.self_id):
      return int(seg.data["qq"])

  if target_str.isdigit():
    return int(target_str)

  members = await bot.get_group_member_list(group_id=group_id)
  for m in members:
    card = m.get("card", "")
    nickname = m.get("nickname", "")
    if target_str and (target_str == card or target_str == nickname or target_str in card or target_str in nickname):
      return m["user_id"]

  return None


# ─── NoneBot 命令入口 ─────────────────────────────────────


ban = on_command("禁言")


@ban.handle()
async def group_ban(bot: Bot, event: GroupMessageEvent, ats=Ats(), args=Args(0, 2)):
  target_id: int | None = None
  duration = 1

  if ats:
    target_id = ats[0]
    if target_id == config.bot.owner_id:
      await ban.finish("大胆妖孽! 你想对我爹做什么!")
    if args:
      try:
        duration = int(args[0])
      except (ValueError, IndexError):
        pass
  elif args:
    target_str = args[0] if args else ""
    target_id = await resolve_target(bot, event.group_id, event, target_str)
    if target_id == config.bot.owner_id:
      await ban.finish("大胆妖孽! 你想对我爹做什么!")
    if len(args) > 1:
      try:
        duration = int(args[1])
      except ValueError:
        pass
    elif target_str and not target_str.isdigit():
      # 尝试从剩余文本提取数字作为时长（如 "张三3分钟"）
      import re
      m = re.search(r"(\d+)", " ".join(args[1:]) if len(args) > 1 else "")
      if m:
        duration = int(m.group(1))

  if not target_id:
    await ban.finish("请指定禁言目标（@/QQ号/昵称）")

  result = await do_ban(bot, event.group_id, target_id, duration)
  await ban.finish(result)
