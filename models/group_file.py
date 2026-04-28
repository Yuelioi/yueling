from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class GroupFileRecord(Base):
  __tablename__ = "group_files"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  group_id: Mapped[int] = mapped_column(Integer, nullable=False)
  file_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
  file_name: Mapped[str] = mapped_column(String(128), nullable=False)
  busid: Mapped[int] = mapped_column(Integer, nullable=False)
  file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
  upload_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
  dead_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
  modify_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
  download_times: Mapped[int | None] = mapped_column(Integer, nullable=True)
  uploader: Mapped[int | None] = mapped_column(Integer, nullable=True)
  uploader_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
