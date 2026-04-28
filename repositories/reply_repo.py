from sqlalchemy import delete, select

from core.database import async_session
from models import AutoReply


class ReplyRepository:

  async def get_all(self) -> list[AutoReply]:
    async with async_session() as session:
      stmt = select(AutoReply)
      result = await session.execute(stmt)
      return list(result.scalars().all())

  async def add(self, qq: int, keyword: str, reply: str, group: str = "") -> bool:
    async with async_session() as session:
      record = AutoReply(qq=qq, keyword=keyword, reply=reply, group=group or None)
      session.add(record)
      try:
        await session.commit()
        return True
      except Exception:
        await session.rollback()
        return False

  async def delete_by_id(self, reply_id: int) -> bool:
    async with async_session() as session:
      stmt = delete(AutoReply).where(AutoReply.id == reply_id)
      result = await session.execute(stmt)
      await session.commit()
      return result.rowcount > 0


reply_repo = ReplyRepository()
