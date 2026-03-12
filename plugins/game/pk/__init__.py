from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from common.base.Depends import At
from plugins.game.pk.const import SIGN_MONEY, SIGN_POWER
from plugins.game.pk.db import udb
from plugins.game.pk.utils import pk_generator

pk = on_command("pk")
sign = on_command("签到")


@pk.handle()
async def _pk(event: GroupMessageEvent, user=At()):
  attacker = udb.get_user(user_id=event.user_id)
  defender = udb.get_user(user_id=user)

  result = pk_generator(attacker.nickname, defender=defender.nickname, win_rate=0.5, is_win=True)  # type: ignore
  if result:
    await pk.finish(result)
  else:
    logger.warning(f"pk_generator 返回空结果: {event.user_id} vs {user}")


@sign.handle()
async def _sign(event: GroupMessageEvent):
  udb.add_money(user_id=event.user_id, money=SIGN_MONEY)
  udb.add_power(user_id=event.user_id, power=SIGN_POWER)
  await sign.finish("签到成功！")
