import asyncio
import os
import time
from typing import cast

import aiofiles
from fastapi import APIRouter
from nonebot import get_bot

from plugins.group.file.utils import get_qq_folder_files, get_root

file = APIRouter()

from fastapi import APIRouter, File, UploadFile
from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Bot

from common.biz import result
from common.config import config


@file.get("/files", response_model=dict)
async def _files(group_id: int, user_id: int, skip_root: bool = True, ignore_extensions: list[str] = []):
  if user_id != 435826135:
    return result.success({"message": ""})
  bot = cast(Bot, get_bot())
  root = await get_root(bot=bot, group_id=group_id)
  data = await get_qq_folder_files(bot=bot, group_id=group_id, root=root)

  return result.success(data)


@file.get("/file")
async def file_info(group_id: int, user_id: int, file_id: str, busid: int):
  if user_id != 435826135:
    return result.success({"message": ""})
  bot = cast(Bot, get_bot())

  data = await bot.get_group_file_url(group_id=group_id, file_id=file_id, busid=busid)
  return result.success(data)


# folder 要传id 不传默认根目录
@file.post("/file")
async def file_upload(group_id: int, user_id: int, folder: str = "", file: UploadFile = File(...)):
  if user_id != 435826135:
    return result.success({"message": ""})
  bot = cast(Bot, get_bot())
  filename = file.filename or f"{time.time()}.tmp"  # 使用时间戳作为默认文件名
  filepath = config.resource.tmp / filename

  file_content = await file.read()
  if not file_content:
    return result.success({"message": "文件内容为空，无法上传。"})
  if not filepath.exists():
    async with aiofiles.open(filepath, "wb") as buffer:
      await buffer.write(file_content)

  await bot.upload_group_file(group_id=group_id, file=str(filepath), name=filename)

  await asyncio.to_thread(os.remove, str(filepath))
  return result.success({})
