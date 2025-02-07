import asyncio
import time
from pathlib import Path

import aiofiles
import aiohttp
from nonebot import get_driver, logger
from nonebot.adapters.onebot.v11 import Bot

from common.config import config
from plugins.group.file.models import LocalFile, QQFile, QQFolder
from plugins.group.file.utils import (
  fetch_file_url,
  get_qq_folder_files,
  get_qq_root_files,
  get_root,
)


class Config:
  def __init__(self):
    self.contain_root: bool = False
    self.contain_folder: bool = True
    self.ignore_extensions: list[str] = ["gif", "png", "jpg", "mp4"]  # 不带.了
    self.backup_dir: Path = config.resource.groups  # 本地储存的根目录


# 备份事件
class BackupEventInfo:
  def __init__(self):
    self.backup_directory: Path = Path()  # 备份根文件夹, 本地当前群文件夹
    self.qqfile_entries: list[QQFile] = []  # QQ文件集合
    self.qqfolder_entries: list[QQFolder] = []  # QQ文件夹集合
    self.is_processing = False  # 处理状态 禁止同时执行多个任务
    self.reset()

  def reset(self) -> None:
    self.backup_directory = Path()
    self.qqfile_entries.clear()
    self.qqfolder_entries.clear()
    self.success_count = 0
    self.failed_files = []
    self.start_time = time.time()  # 任务开始时间
    self.duration = 0.0  # 任务消耗时长，单位：秒

  # 开始任务
  def start(self, backup_directory: Path):
    self.reset()
    self.backup_directory = backup_directory
    self.is_processing = True
    if not self.backup_directory.exists():
      self.backup_directory.mkdir(parents=True)

  def finish(self):
    self.is_processing = False


class BackupManager:
  def __init__(self):
    self.config = Config()
    self.event_info = BackupEventInfo()

  def init(self):
    config = get_driver().config.model_dump()
    self.config.ignore_extensions = config.get("backup_qq_file_ignore", self.config.ignore_extensions)

  async def collections(self, bot: Bot, group_id: int, contain_root=None, contain_folder=None, ignore_extensions=None):
    """
    contain_root: 包含根目录(不填走配置) False
    contain_folder: 包含内部文件夹(不填走配置) True
    ignore_extensions: 忽略根目录的文件后缀(不填走配置) 不用带.
    """

    if contain_root is None:
      contain_root = self.config.contain_root
    if contain_folder is None:
      contain_folder = self.config.contain_folder
    if ignore_extensions is None:
      ignore_extensions = self.config.ignore_extensions

    folders = []
    files = []

    root = await get_root(bot, group_id)
    if contain_root:
      _folders, _files = await get_qq_root_files(root, ignore_extensions)
      folders.extend(_folders)
      files.extend(_files)

    if contain_folder:
      _folders, _files = await get_qq_folder_files(bot, group_id, root)
      folders.extend(_folders)
      files.extend(_files)
    self.event_info.qqfile_entries = files
    self.event_info.qqfolder_entries = folders

  # 备份群文件
  async def backup(self, bot: Bot, toDownloadFiles: list[QQFile]):
    await asyncio.gather(*(self.save_file(bot, file_info) for file_info in toDownloadFiles))
    self.event_info.duration = round(time.time() - self.event_info.start_time, 2)

  async def save_file(self, bot: Bot, file: QQFile):
    file_path = Path(self.event_info.backup_directory, file.get("folder_name", ""), file["file_name"])
    file_relative_path = f"{file.get('folder_name','')}/{file['file_name']}"

    try:
      await self.download(bot=bot, file_path=file_path, file=file)
      self.event_info.success_count += 1
    except Exception as e:
      self.event_info.failed_files.append(file_relative_path)
      logger.error(f"下载文件失败: {file_relative_path} {e}")

  # 下载文件
  async def download(self, bot: Bot, file_path: Path, file: QQFile):
    async with aiofiles.open(file_path, "wb") as mfile:
      url = await fetch_file_url(bot, file)
      if url:
        async with aiohttp.ClientSession() as session:
          async with session.get(url) as req:
            if req.status == 200:
              await mfile.write(await req.read())
            else:
              raise Exception(f"无法获取文件: {url}，状态码: {req.status}")

  # 恢复群文件
  async def recover(self, bot: Bot, group_id: int, toUploadFiles: list[LocalFile], need_create_folder_names: list[str]):
    if need_create_folder_names:
      for folder_name in need_create_folder_names:
        await bot.create_group_file_folder(group_id=group_id, name=folder_name, parent_id="/")
        await asyncio.sleep(0.5)

    # 更新群文件夹数据
    root = await bot.get_group_root_files(group_id=group_id)
    self.event_info.qqfolder_entries.clear()
    folders = root.get("folders", [])
    print(folders)
    self.event_info.qqfolder_entries.extend(QQFolder(fd) for fd in folders)

    folder_ids = {fd.get("folder_name", ""): fd["folder_id"] for fd in self.event_info.qqfolder_entries}

    # 上传文件
    for f in toUploadFiles:
      try:
        await bot.upload_group_file(group_id=group_id, file=f["file_path"], name=f["file_name"], folder=folder_ids.get(f.get("folder_name"), None))
        self.event_info.success_count += 1
      except Exception as e:
        self.event_info.failed_files.append(f"{f.get('folder_name')}/{f['file_name']}")
        logger.error(f"上传文件失败:{f.get('folder_name')}/{f['file_name']} 错误: {e}")
    self.event_info.duration = round(time.time() - self.event_info.start_time, 2)

  async def clear(self, bot: Bot, group_id: int, exts):
    files_to_delete = [file for file in self.event_info.qqfile_entries if file["file_name"].lower().split(".")[-1] in exts]
    for file in files_to_delete:
      await bot.call_api("delete_group_file", group_id=group_id, file_id=file["file_id"], busid=file["busid"])
      self.event_info.success_count += 1

    self.event_info.duration = round(time.time() - self.event_info.start_time, 2)


bm = BackupManager()
bm.init()
