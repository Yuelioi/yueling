from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class PkUser(Base):
  __tablename__ = "pk_users"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  user_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
  nickname: Mapped[str] = mapped_column(String, unique=True, nullable=False)
  power: Mapped[int] = mapped_column(Integer, default=0)
  money: Mapped[int] = mapped_column(Integer, default=0)


class PkStatus(Base):
  __tablename__ = "pk_status"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  user_id: Mapped[int] = mapped_column(Integer, nullable=False)
  name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
  description: Mapped[str] = mapped_column(String, nullable=False)
  duration: Mapped[str | None] = mapped_column(String, nullable=True)


class PkBuff(Base):
  __tablename__ = "pk_buffs"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  user_id: Mapped[int] = mapped_column(Integer, nullable=False)
  name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
  description: Mapped[str] = mapped_column(String, nullable=False)
  duration: Mapped[str | None] = mapped_column(String, nullable=True)
