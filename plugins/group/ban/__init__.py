from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot_plugin_alconna import Alconna, Args, At, on_alconna

from common.Alc.Alc import pm, ptc
from common.Alc.Permission import Bot_Checker, User_Checker
from common.base.Permission import admin_validate

__plugin_meta__ = pm(
  name="禁言",
  description="禁言群友, 需要管理权限",
  usage="""禁言 + @群友""",
  group="群管",
)
_ban = Alconna("禁言", Args["member", At]["duration?", int], meta=ptc(__plugin_meta__))

ban = on_alconna(_ban)


@ban.assign("$main", additional=User_Checker & Bot_Checker)
async def _group_ban(
  bot: Bot,
  event: GroupMessageEvent,
  member: At,
  duration: int = 1,
):
  if member.target == "435826135":
    await ban.finish("大胆妖孽! 你想对我爹做什么!")
  is_admin = await admin_validate(bot=bot, group_id=event.group_id, user_id=int(member.target))

  if is_admin:
    await ban.finish("管理何必为难管理")

  await bot.set_group_ban(
    group_id=event.group_id,
    user_id=int(member.target),
    duration=int(duration) * 60,
  )
