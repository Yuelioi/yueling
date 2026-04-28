from sqlalchemy import Integer, String, Float, Index
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class MessageStat(Base):
  __tablename__ = "message_stats"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  group_id: Mapped[int] = mapped_column(Integer, nullable=False)
  user_id: Mapped[int] = mapped_column(Integer, nullable=False)
  nickname: Mapped[str] = mapped_column(String(64), nullable=False, default="")
  timestamp: Mapped[float] = mapped_column(Float, nullable=False)

  __table_args__ = (
    Index("ix_msgstat_group_ts", "group_id", "timestamp"),
  )
