"""
本地文件数据访问层
"""
import asyncio
import os
import shutil
from pathlib import Path
from typing import Optional

import aiofiles
import httpx
from nonebot import logger

from core.http import get_client
from .exceptions import FileDownloadException


class LocalFileRepository:
    """本地文件操作仓储"""

    async def download_file(
        self,
        file_path: Path,
        file_url: str,
        timeout: float = 30.0
    ) -> None:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            client = get_client()
            response = await client.get(file_url, timeout=timeout)
            if response.status_code != 200:
                raise FileDownloadException(
                    file_path.name,
                    status_code=response.status_code
                )

            async with aiofiles.open(file_path, "wb") as f:
                await f.write(response.content)

            logger.debug(f"文件下载成功: {file_path}")

        except httpx.HTTPError as e:
            raise FileDownloadException(
                file_path.name,
                reason=f"网络错误: {e}"
            )
        except FileDownloadException:
            raise
        except Exception as e:
            raise FileDownloadException(
                file_path.name,
                reason=str(e)
            )

    def get_local_files(self, directory: Path) -> dict[str, Path]:
        if not directory.exists():
            return {}

        files = {}
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = Path(dirpath) / filename
                relative_path = file_path.relative_to(directory)
                key = str(relative_path)
                files[key] = file_path

        return files

    def create_local_folders(self, directory: Path, folder_names: list[str]) -> None:
        for folder_name in folder_names:
            if folder_name:
                folder_path = directory / folder_name
                folder_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"创建本地文件夹: {folder_path}")

    async def delete_directory(self, directory: Path) -> None:
        try:
            if directory.exists():
                await asyncio.to_thread(shutil.rmtree, directory)
                logger.info(f"目录删除成功: {directory}")
        except Exception as e:
            logger.error(f"目录删除失败 {directory}: {e}")
            raise

    async def delete_file(self, file_path: Path) -> None:
        try:
            if file_path.exists():
                await asyncio.to_thread(file_path.unlink)
                logger.debug(f"文件删除成功: {file_path}")
        except Exception as e:
            logger.error(f"文件删除失败 {file_path}: {e}")
            raise

    def get_backup_info(self, backup_dir: Path) -> Optional[dict]:
        if not backup_dir.exists():
            return None

        file_count = 0
        total_size = 0

        for dirpath, _, filenames in os.walk(backup_dir):
            for filename in filenames:
                file_path = Path(dirpath) / filename
                file_count += 1
                total_size += file_path.stat().st_size

        return {
            'file_count': file_count,
            'total_size': total_size,
            'created_time': backup_dir.stat().st_ctime if backup_dir.exists() else None
        }


local_file_repo = LocalFileRepository()
