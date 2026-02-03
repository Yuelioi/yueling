"""
本地文件数据访问层
"""
import os
import shutil
from pathlib import Path
from typing import Optional

import aiofiles
import aiohttp
from nonebot import logger

from .exceptions import FileDownloadException
from .models_domain import LocalFile, QQFile
from aiohttp import ClientTimeout


class LocalFileRepository:
    """本地文件操作仓储"""
    
    async def download_file(
        self,
        file_path: Path,
        file_url: str,
        timeout: ClientTimeout = ClientTimeout(total=30)
    ) -> None:
        """
        下载文件
        
        Args:
            file_path: 本地保存路径
            file_url: 远程文件URL
            timeout: 超时时间（秒）
        
        Raises:
            FileDownloadException: 下载失败
        """
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url, timeout=timeout) as req:
                    if req.status != 200:
                        raise FileDownloadException(
                            file_path.name,
                            status_code=req.status
                        )
                    
                    async with aiofiles.open(file_path, "wb") as f:
                        await f.write(await req.read())
                    
                    logger.debug(f"文件下载成功: {file_path}")
        
        except aiohttp.ClientError as e:
            raise FileDownloadException(
                file_path.name,
                reason=f"网络错误: {str(e)}"
            )
        except Exception as e:
            raise FileDownloadException(
                file_path.name,
                reason=str(e)
            )
    
    def get_local_files(self, directory: Path) -> dict[str, Path]:
        """
        获取本地目录中的所有文件
        
        Returns:
            {相对路径: 绝对路径} 的字典
        """
        if not directory.exists():
            return {}
        
        files = {}
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = Path(dirpath) / filename
                relative_path = file_path.relative_to(directory)
                key = str(relative_path)  # 用正斜杠作为分隔符
                files[key] = file_path
        
        return files
    
    def create_local_folders(self, directory: Path, folder_names: list[str]) -> None:
        """创建本地文件夹"""
        for folder_name in folder_names:
            if folder_name:  # 跳过空字符串
                folder_path = directory / folder_name
                folder_path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"创建本地文件夹: {folder_path}")
    
    async def delete_directory(self, directory: Path) -> None:
        """
        删除整个目录
        
        Args:
            directory: 要删除的目录
        """
        try:
            if directory.exists():
                # 使用线程池删除，避免阻塞
                import asyncio
                await asyncio.to_thread(shutil.rmtree, directory)
                logger.info(f"目录删除成功: {directory}")
        except Exception as e:
            logger.error(f"目录删除失败 {directory}: {e}")
            raise
    
    async def delete_file(self, file_path: Path) -> None:
        """删除单个文件"""
        try:
            if file_path.exists():
                import asyncio
                await asyncio.to_thread(file_path.unlink)
                logger.debug(f"文件删除成功: {file_path}")
        except Exception as e:
            logger.error(f"文件删除失败 {file_path}: {e}")
            raise
    
    def get_backup_info(self, backup_dir: Path) -> Optional[dict]:
        """
        获取备份信息
        
        Returns:
            {
                'file_count': 文件数,
                'total_size': 总大小(字节),
                'created_time': 创建时间
            }
        """
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


# 全局仓储实例
local_file_repo = LocalFileRepository()