from collections import deque
from pathlib import Path

from nonebot.adapters.onebot.v11 import Bot

from plugins.group.file.models import QQFile, QQFilesResp, QQFolder


async def fetch_file_url(bot: Bot, file: QQFile):
  file_info = await bot.get_group_file_url(group_id=file["group_id"], file_id=file["file_id"], busid=file["busid"])
  return file_info["url"]


async def get_root(bot: Bot, group_id: int) -> QQFilesResp:
  return await bot.get_group_root_files(group_id=group_id)


# 收集根目录群文件/文件夹
async def get_qq_root_files(root: QQFilesResp, ignore_extensions: list[str]) -> tuple[list[QQFolder], list[QQFile]]:
  file_entries = []
  # 备份临时文件
  qq_files = root.get("files", [])
  for qq_file in qq_files:
    if not Path(qq_file["file_name"]).suffix.lower().endswith(tuple(ignore_extensions)):
      file_entries.append(QQFile(qq_file))

  folders = root.get("folders", [])

  return folders, file_entries


# 收集群文件
async def get_qq_folder_files(
  bot: Bot,
  group_id: int,
  root: QQFilesResp,
) -> tuple[list[QQFolder], list[QQFile]]:
  file_entries = []

  folders = root.get("folders", [])

  # 广度优先搜索
  dq = deque(folders)
  while dq:
    folder = dq.popleft()
    root = await bot.get_group_files_by_folder(group_id=group_id, folder_id=folder["folder_id"])
    files = root.get("files", [])
    file_entries.extend(QQFile(file, folder_name=folder["folder_name"]) for file in files)

  return folders, file_entries


def get_folder(folders: list[QQFolder], folder_name: str):
  for fd in folders:
    if fd["folder_name"] == folder_name:
      return fd
