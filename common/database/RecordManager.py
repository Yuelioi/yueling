from dataclasses import asdict, dataclass, field
from datetime import datetime

from nonebot import logger
from sqlalchemy import Column, DateTime, Integer, String, extract, func

from common.config import config
from common.database.DBBase import DBManagerBase, Element


# tag reply
@dataclass
class Record(Element):
  qq: int = 0
  last_record_time: datetime = field(default_factory=datetime.now)


class ReplyDataManager(DBManagerBase):
  def _create_table_fields(self):
    self.table_fields = [
      Column("id", Integer, primary_key=True),
      Column("qq", Integer),
      Column("target", String(128), nullable=True),
      Column("last_record_time", DateTime(), nullable=True),
    ]

  def check_record(self, record: Record):
    try:
      # 获取当天日期
      today_date = datetime.now().date()

      # 查询条件，检查当天是否已经有相同内容的记录
      existing_records = self.conn.execute(
        self.table.select().where(
          (self.table.c.qq == record.qq) & (func.date(self.table.c.last_record_time) == today_date),
        )
      ).fetchall()

      if existing_records:
        # 当天已经有相同内容的记录，返回 False
        return False
      else:
        # 当天没有相同内容的记录，返回 True
        return True

    except Exception as e:
      logger.error("check record error:", e)
      return False

  def insert_data(self, record: Record):
    """插入单个文件数据"""
    self.check_record(record)
    try:
      self.conn.execute(self.table.insert().values(**asdict(record)))
      self.conn.commit()
      return True
    except Exception as e:
      logger.error("record insert error:", e)
      return False

  def get_records_for_current_month(self, record: Record):
    try:
      current_date = datetime.now()
      current_month = current_date.month

      # 查询条件，筛选出本月的打卡记录
      result = self.conn.execute(
        self.table.select().where((self.table.c.qq == record.qq) & (extract("month", self.table.c.last_record_time) == current_month))
      ).fetchall()

      return self.to_dicts(result)
    except Exception as e:
      logger.error("get_records error:", e)
      return []

  def get_records_for_current_week(self, qq: int):
    try:
      # 获取当前日期
      current_date = datetime.now()

      # 提取当前周
      current_week = current_date.isocalendar()[1]

      # 查询条件，筛选出本周的打卡记录
      result = self.conn.execute(
        self.table.select().where((self.table.c.qq == qq) & (extract("week", self.table.c.last_record_time) == current_week))
      ).fetchall()

      return self.to_dicts(result)
    except Exception as e:
      logger.error("get_records error:", e)
      return False


rcm = ReplyDataManager(db_path=config.data.database, table_name="record")
