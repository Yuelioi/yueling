from sqlalchemy import delete, select

from core.database import async_session
from models import GroupFileRecord


class GroupFileRepository:

  async def insert(self, **kwargs) -> bool:
    async with async_session() as session:
      record = GroupFileRecord(**kwargs)
      session.add(record)
      try:
        await session.commit()
        return True
      except Exception:
        await session.rollback()
        return False

  async def get_by_group(self, group_id: int) -> list[GroupFileRecord]:
    async with async_session() as session:
      stmt = select(GroupFileRecord).where(GroupFileRecord.group_id == group_id)
      result = await session.execute(stmt)
      return list(result.scalars().all())

  async def get_by_file_id(self, file_id: str) -> GroupFileRecord | None:
    async with async_session() as session:
      stmt = select(GroupFileRecord).where(GroupFileRecord.file_id == file_id)
      result = await session.execute(stmt)
      return result.scalar_one_or_none()

  async def delete_by_group(self, group_id: int) -> int:
    async with async_session() as session:
      stmt = delete(GroupFileRecord).where(GroupFileRecord.group_id == group_id)
      result = await session.execute(stmt)
      await session.commit()
      return result.rowcount


group_file_repo = GroupFileRepository()
