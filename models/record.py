from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class ClockInRecord(Base):
  __tablename__ = "clock_in_records"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  qq: Mapped[int] = mapped_column(Integer, nullable=False)
  target: Mapped[str | None] = mapped_column(String(128), nullable=True)
  last_record_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
