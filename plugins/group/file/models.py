from typing import TypedDict


class LocalFile(TypedDict):
  file_path: str
  folder_name: str
  file_name: str


class QQFile(TypedDict):
  group_id: int
  file_name: str
  file_id: str
  busid: str
  file_size: int
  folder_name: str


class QQFolder(TypedDict):
  group_id: int
  folder_name: str
  folder_id: str


class QQFilesResp(TypedDict):
  files: list[QQFile]
  folders: list[QQFolder]
