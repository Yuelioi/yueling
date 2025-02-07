from datetime import datetime

from sqlalchemy import Column, Integer, String

from common.config import config

from .DBBase import DBManagerBase


class GFM(DBManagerBase):
  """QQ群文件管理"""

  def _create_table_fields(self):
    """初始化表"""
    self.table_fields = [
      Column("id", Integer, primary_key=True),
      Column("group_id", Integer),
      Column("file_id", String(128), nullable=False, unique=True),
      Column("file_name", String(128), nullable=False),
      Column("busid", Integer, nullable=False),
      Column("file_size", Integer),
      Column("upload_time", Integer, default=datetime.utcnow),
      Column("dead_time", Integer),
      Column("modify_time", Integer, default=datetime.utcnow),
      Column("download_times", Integer),
      Column("uploader", Integer),
      Column("uploader_name", String(128)),
    ]

  def delete_group_data(self, group_id: int):
    """Clear Group Data By Group id

    Args:
        group_id (int): _description_
    """
    self.conn.execute(self.table.delete().where(self.table.c.group_id == group_id))
    self.conn.commit()

  def get_files_info_by_name(self, filename: str, num: int = 3):
    """根据文件关键词 获取文件列表"""
    query = self.table.select().where(self.table.c.file_name.like(f"%{filename}%")).limit(num)

    if result := self.conn.execute(query).fetchall():
      return self.to_dicts(result)

    else:
      return []

  def remove_file(self, file_id: int):
    """根据文件id删除该数据(可能文件损坏/被删除)"""
    try:
      delete_query = self.table.delete().where(self.table.c.id == file_id)
      self.conn.execute(delete_query)
      self.conn.commit()
      return f"成功删除文件ID为 {file_id} 的数据"
    except Exception as e:
      return f"删除文件ID为 {file_id} 的数据时发生错误：{e}"


gfm = GFM(db_path=config.data.database, table_name="groupfiles")
