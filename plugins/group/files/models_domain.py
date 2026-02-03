"""
数据模型定义 - 使用Pydantic提供类型检查和验证
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, validator


class QQFile(BaseModel):
    """QQ群文件模型"""
    group_id: int
    file_name: str
    file_id: str
    busid: int
    file_size: int
    folder_name: str = ""  # 默认为根目录
    
    class Config:
        frozen = True  # 不可变，适合作为值对象


class QQFolder(BaseModel):
    """QQ群文件夹模型"""
    group_id: int
    folder_name: str
    folder_id: str
    
    class Config:
        frozen = True


class LocalFile(BaseModel):
    """本地文件模型"""
    file_path: Path
    file_name: str
    folder_name: str = ""
    
    @validator("file_path", pre=True)
    def validate_file_path(cls, v):
        return Path(v)
    
    class Config:
        frozen = True


class FileQueryInfo(BaseModel):
    file_name: str
    folder: str
    size: int  # bytes

class QueryResult(BaseModel):
    files: list[FileQueryInfo]

class FileReference(BaseModel):
    """文件引用（用于对比云端和本地）"""
    folder_name: str
    file_name: str
    
    def __hash__(self):
        return hash((self.folder_name, self.file_name))


class TaskResult(BaseModel):
    """任务执行结果"""
    success_count: int = 0
    failed_files: list[str] = Field(default_factory=list)
    duration: float = 0.0  # 秒
    error_message: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        return self.error_message is None


class BackupTaskResult(TaskResult):
    """备份任务结果"""
    total_files: int = 0
    download_count: int = 0


class RecoveryTaskResult(TaskResult):
    """恢复任务结果"""
    total_local_files: int = 0
    upload_count: int = 0
    created_folders: list[str] = Field(default_factory=list)


class ClearTaskResult(TaskResult):
    """清理任务结果"""
    target_extensions: list[str] = Field(default_factory=list)


class OrganizeTaskResult(TaskResult):
    """整理任务结果"""
    target_folder: str = ""
    target_extensions: list[str] = Field(default_factory=list)
    created_folder: bool = False


class GroupFileSnapshot(BaseModel):
    """群文件快照（用于缓存）"""
    group_id: int
    files: list[QQFile] = Field(default_factory=list)
    folders: list[QQFolder] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @property
    def is_stale(self, max_age_seconds: int = 300) -> bool:
        """检查快照是否过期"""
        return (datetime.now() - self.timestamp).total_seconds() > max_age_seconds