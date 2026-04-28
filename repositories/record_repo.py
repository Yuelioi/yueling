from datetime import datetime

from sqlalchemy import select

from core.database import async_session
from models import ClockInRecord


class RecordRepository:

  async def get_record(self, qq: int) -> ClockInRecord | None:
    async with async_session() as session:
      stmt = select(ClockInRecord).where(ClockInRecord.qq == qq)
      result = await session.execute(stmt)
      return result.scalar_one_or_none()

  async def check_today(self, qq: int) -> bool:
    record = await self.get_record(qq)
    if not record or not record.last_record_time:
      return False
    return record.last_record_time.date() == datetime.now().date()

  async def clock_in(self, qq: int) -> bool:
    if await self.check_today(qq):
      return False
    async with async_session() as session:
      stmt = select(ClockInRecord).where(ClockInRecord.qq == qq)
      result = await session.execute(stmt)
      record = result.scalar_one_or_none()
      if record:
        record.last_record_time = datetime.now()
      else:
        record = ClockInRecord(qq=qq, last_record_time=datetime.now())
        session.add(record)
      await session.commit()
      return True


record_repo = RecordRepository()
