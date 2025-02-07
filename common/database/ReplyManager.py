from dataclasses import dataclass

from sqlalchemy import Column, Integer, String

from common.config import config
from common.database.DBBase import DBManagerBase
from common.models import Element


# tag reply
@dataclass
class Reply(Element):
  qq: int = 0
  keyword: str = ""
  reply: str = ""
  group: list[str] | str | None = None


class ReplyDataManager(DBManagerBase):
  def _create_table_fields(self):
    self.table_fields = [
      Column("id", Integer, primary_key=True),
      Column("qq", Integer),
      Column("keyword", String(128), nullable=True, unique=True),
      Column("reply", String(1024), nullable=True),
      Column("group", String(128), nullable=True),
    ]

  def get_reply_data(self):
    try:
      result = self.conn.execute(self.table.select()).fetchall()
      return self.to_dicts(result)
    except:
      return False

  def delete_reply_data(self, reply_id: int):
    try:
      self.conn.execute(self.table.delete().where(self.table.c.id == reply_id))
      self.conn.commit()
      return True
    except:
      return False


rpm = ReplyDataManager(db_path=config.data.database, table_name="reply")
