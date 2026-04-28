from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class PixivImage(Base):
  __tablename__ = "pixiv_image"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  img_id: Mapped[str] = mapped_column(String, nullable=False)
  hash: Mapped[str] = mapped_column(String, nullable=False)
  title: Mapped[str] = mapped_column(String, nullable=False)
  description: Mapped[str | None] = mapped_column(String, nullable=True)
  tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
  url: Mapped[str] = mapped_column(String, nullable=False)
  meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
  urls: Mapped[dict | None] = mapped_column(JSON, nullable=True)
  page_count: Mapped[int] = mapped_column(Integer, default=1)
  user_id: Mapped[str] = mapped_column(String, nullable=False)
  user_name: Mapped[str] = mapped_column(String, nullable=False)
  user_avatar: Mapped[str | None] = mapped_column(String, nullable=True)
  width: Mapped[int] = mapped_column(Integer, nullable=False)
  height: Mapped[int] = mapped_column(Integer, nullable=False)
  bookmarks: Mapped[int] = mapped_column(Integer, nullable=False)
  views: Mapped[int | None] = mapped_column(Integer, nullable=True)
  source: Mapped[str] = mapped_column(String, nullable=False)
  x_restrict: Mapped[int] = mapped_column(Integer, nullable=False)
  ai_type: Mapped[int] = mapped_column(Integer, nullable=False)
  created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
  updated: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
  size_kb: Mapped[int] = mapped_column(Integer, default=0)
  file_ext: Mapped[str] = mapped_column(String, default="")
  score: Mapped[int] = mapped_column(Integer, default=0)
