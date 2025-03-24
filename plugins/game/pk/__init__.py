from nonebot import on_command
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
  print(result)


@sign.handle()
def _sign(event: GroupMessageEvent):
  udb.add_money(user_id=event.user_id, money=SIGN_MONEY)
  udb.add_power(user_id=event.user_id, power=SIGN_POWER)
