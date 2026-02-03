"""
自定义异常定义
"""


class FileManagementException(Exception):
    """文件管理基异常"""
    pass


class BackupException(FileManagementException):
    """备份异常"""
    pass


class RecoveryException(FileManagementException):
    """恢复异常"""
    pass


class FileDownloadException(BackupException):
    """文件下载异常"""
    
    def __init__(self, file_name: str, status_code: int = -1, reason: str = "unkown"):
        self.file_name = file_name
        self.status_code = status_code
        if status_code:
            msg = f"无法下载文件 {file_name}，状态码: {status_code}"
        else:
            msg = f"无法下载文件 {file_name}: {reason or '未知错误'}"
        super().__init__(msg)


class FileUploadException(RecoveryException):
    """文件上传异常"""
    
    def __init__(self, file_name: str, reason: str = "unkown"):
        msg = f"无法上传文件 {file_name}: {reason or '未知错误'}"
        self.file_name = file_name
        super().__init__(msg)


class FolderOperationException(FileManagementException):
    """文件夹操作异常"""
    
    def __init__(self, folder_name: str, operation: str, reason: str = "unkown"):
        msg = f"文件夹操作失败 [{operation}] {folder_name}: {reason or '未知错误'}"
        self.folder_name = folder_name
        super().__init__(msg)


class BackupStateException(FileManagementException):
    """备份状态异常"""
    pass


class TaskExecutionException(FileManagementException):
    """任务执行异常"""
    pass


class InvalidArgumentException(FileManagementException):
    """参数异常"""
    pass


class BackupNotFoundError(FileManagementException):
    """备份文件不存在"""
    pass