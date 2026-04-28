from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class AutoReply(Base):
  __tablename__ = "auto_replies"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  qq: Mapped[int] = mapped_column(Integer, nullable=False)
  keyword: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
  reply: Mapped[str | None] = mapped_column(String(1024), nullable=True)
  group: Mapped[str | None] = mapped_column(String(128), nullable=True)
