from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from core.deps import At
from repositories.pk_repo import pk_repo
from plugins.game.pk.utils import pk_generator

pk = on_command("pk")
sign = on_command("签到")

SIGN_MONEY = 10
SIGN_POWER = 5


@pk.handle()
async def _pk(event: GroupMessageEvent, user=At()):
  attacker = await pk_repo.get_user(user_id=event.user_id)
  defender = await pk_repo.get_user(user_id=user)

  if not attacker:
    await pk.finish("你还没有注册，请先签到")
  if not defender:
    await pk.finish("对方还没有注册")

  result = await pk_generator(attacker.nickname, defender=defender.nickname, win_rate=0.5, is_win=True)
  if result:
    await pk.finish(result)
  else:
    logger.warning(f"pk_generator 返回空结果: {event.user_id} vs {user}")


@sign.handle()
async def _sign(event: GroupMessageEvent):
  user = await pk_repo.get_user(event.user_id)
  if not user:
    info = await event.bot.get_group_member_info(group_id=event.group_id, user_id=event.user_id)  # type: ignore
    nickname = info.get("card") or info.get("nickname") or str(event.user_id)
    await pk_repo.register(event.user_id, nickname)
    await sign.finish("注册成功！获得初始战力和金币")

  await pk_repo.update_money(event.user_id, SIGN_MONEY)
  await pk_repo.update_power(event.user_id, SIGN_POWER)
  await sign.finish("签到成功！")
