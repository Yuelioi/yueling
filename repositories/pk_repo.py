from sqlalchemy import select

from core.database import async_session
from models import PkUser

REGISTER_POWER = 100
REGISTER_MONEY = 1000


class PkRepository:

  async def get_user(self, user_id: int) -> PkUser | None:
    async with async_session() as session:
      stmt = select(PkUser).where(PkUser.user_id == user_id)
      result = await session.execute(stmt)
      return result.scalar_one_or_none()

  async def register(self, user_id: int, nickname: str) -> PkUser:
    async with async_session() as session:
      user = PkUser(user_id=user_id, nickname=nickname, power=REGISTER_POWER, money=REGISTER_MONEY)
      session.add(user)
      await session.commit()
      await session.refresh(user)
      return user

  async def update_power(self, user_id: int, power_delta: int) -> bool:
    async with async_session() as session:
      stmt = select(PkUser).where(PkUser.user_id == user_id)
      result = await session.execute(stmt)
      user = result.scalar_one_or_none()
      if user:
        user.power = max(0, user.power + power_delta)
        await session.commit()
        return True
      return False

  async def update_money(self, user_id: int, money_delta: int) -> bool:
    async with async_session() as session:
      stmt = select(PkUser).where(PkUser.user_id == user_id)
      result = await session.execute(stmt)
      user = result.scalar_one_or_none()
      if user:
        user.money = max(0, user.money + money_delta)
        await session.commit()
        return True
      return False


pk_repo = PkRepository()
