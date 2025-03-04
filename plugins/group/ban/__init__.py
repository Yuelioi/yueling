from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.plugin import PluginMetadata

from common.base.Depends import Args, At
from common.base.Permission import admin_validate

__plugin_meta__ = PluginMetadata(
  name="禁言",
  description="禁言群友, 需要管理权限",
  usage="""禁言 + @群友""",
  extra={"group": "群管"},
)

ban = on_command("禁言")


@ban.handle()
async def group_ban(
  bot: Bot,
  event: GroupMessageEvent,
  at=At(True),
  args=Args(0, 1),
):
  if at == 435826135:
    await ban.finish("大胆妖孽! 你想对我爹做什么!")
  is_admin = await admin_validate(bot=bot, group_id=event.group_id, user_id=at)
  duration = 1
  if args:
    duration = int(args[0])

  if is_admin:
    await ban.finish("管理何必为难管理")

  await bot.set_group_ban(
    group_id=event.group_id,
    user_id=at,
    duration=int(duration) * 60,
  )
