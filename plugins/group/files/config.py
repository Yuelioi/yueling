"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Optional

from nonebot import get_driver


class BackupConfig:
    """备份配置"""
    
    def __init__(self):
        self._config = get_driver().config.model_dump()
        self._backup_dir: Optional[Path] = None
        self._ignore_extensions: Optional[list[str]] = None
        self._max_concurrent_downloads: int = 3
        self._max_concurrent_uploads: int = 2
        self._download_timeout: int = 300  # 秒
        self._upload_timeout: int = 600    # 秒
    
    @property
    def backup_dir(self) -> Path:
        """备份根目录"""
        if self._backup_dir is None:
            from common.config import config
            self._backup_dir = config.resource.groups
        return self._backup_dir
    
    @property
    def ignore_extensions(self) -> list[str]:
        """忽略的文件扩展名（不带.）"""
        if self._ignore_extensions is None:
            # 从配置读取，或使用默认值
            self._ignore_extensions = self._config.get(
                "backup_qq_file_ignore",
                ["gif", "png", "jpg", "jpeg", "mp4", "webm"]
            )
        return self._ignore_extensions or []
    
    @property
    def max_concurrent_downloads(self) -> int:
        """最大并发下载数"""
        return self._max_concurrent_downloads
    
    @property
    def max_concurrent_uploads(self) -> int:
        """最大并发上传数"""
        return self._max_concurrent_uploads
    
    @property
    def download_timeout(self) -> int:
        """下载超时时间（秒）"""
        return self._download_timeout
    
    @property
    def upload_timeout(self) -> int:
        """上传超时时间（秒）"""
        return self._upload_timeout
    
    def get_backup_directory(self, group_id: int) -> Path:
        """获取指定群的备份目录"""
        backup_path = self.backup_dir / str(group_id)
        backup_path.mkdir(parents=True, exist_ok=True)
        return backup_path
    
    def should_ignore_file(self, filename: str) -> bool:
        """检查文件是否应该被忽略"""
        ext = Path(filename).suffix.lower().lstrip(".")
        return ext in self.ignore_extensions


# 全局配置实例
backup_config = BackupConfig()