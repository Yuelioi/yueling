from dataclasses import dataclass

from common.models.base import Element


@dataclass
class GroupFile(Element):
  group_id: int
  file_id: str
  file_name: str
  busid: int
  file_size: int
  upload_time: int
  dead_time: int
  modify_time: int
  download_times: int
  uploader: int
  uploader_name: str
  url: str = ""

  def insert_data(self, element: Element):
    """插入单个文件数据"""
