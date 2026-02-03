"""
备份服务业务逻辑
"""
from pathlib import Path

from aiohttp import ClientTimeout
from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot

from .config import backup_config
from .exceptions import FileDownloadException
from .local_file_repo import local_file_repo
from .models_domain import BackupTaskResult, QQFile
from .qq_file_repo import qq_file_repo
from .task_executor import get_executor


class BackupService:
    """备份服务"""
    
    async def execute_backup(self, bot: Bot, group_id: int) -> BackupTaskResult:
        """
        执行群文件备份
        
        Args:
            bot: Bot实例
            group_id: 群号
        
        Returns:
            BackupTaskResult: 备份结果
        """
        executor = get_executor(group_id)
        
        async def _backup():
            result = BackupTaskResult()
            
            try:
                # 获取备份目录
                backup_dir = backup_config.get_backup_directory(group_id)
                
                # 获取QQ群中的所有文件
                logger.info(f"[{group_id}] 开始扫描群文件...")
                snapshot = await qq_file_repo.get_all_files_recursively(
                    bot=bot,
                    group_id=group_id,
                    include_root=False,
                    include_folders=True
                )
                
                result.total_files = len(snapshot.files)
                logger.info(f"[{group_id}] 扫描完成，发现 {result.total_files} 个文件")
                
                # 创建本地文件夹
                local_file_repo.create_local_folders(
                    backup_dir,
                    sorted({
                      f.folder_name
                      for f in snapshot.files
                      if f.folder_name
                  })
                )
                
                # 获取本地已有文件
                local_files = local_file_repo.get_local_files(backup_dir)
                
                # 计算需要下载的文件
                to_download = [
                    f for f in snapshot.files
                    if self._get_file_key(f) not in local_files
                ]
                
                result.download_count = len(to_download)
                logger.info(f"[{group_id}] 需要下载 {result.download_count} 个文件")
                
                # 执行下载
                if to_download:
                    await self._download_files(bot, backup_dir, to_download, result)
                
                return result
            
            except Exception as e:
                logger.error(f"[{group_id}] 备份异常: {e}", exc_info=True)
                result.error_message = str(e)
                return result
        
        return await executor.execute(_backup, "备份群文件")
    
    async def _download_files(
        self,
        bot: Bot,
        backup_dir: Path,
        files: list[QQFile],
        result: BackupTaskResult
    ) -> None:
        """
        批量下载文件
        
        Args:
            bot: Bot实例
            backup_dir: 本地备份目录
            files: 要下载的文件列表
            result: 结果对象（用于记录进度）
        """
        executor = get_executor(files[0].group_id)
        
        # 生成下载任务
        download_tasks = []
        for file in files:
            file_path = backup_dir / file.folder_name / file.file_name
            download_tasks.append(
                self._download_single_file(bot, file_path, file, result)
            )
        
        # 执行并发下载
        successes, failures = await executor.execute_with_concurrency(
            download_tasks,
            max_workers=backup_config.max_concurrent_downloads,
            task_name="文件下载"
        )
        
        result.success_count = len(successes)
        result.failed_files = failures
    
    async def _download_single_file(
        self,
        bot: Bot,
        file_path: Path,
        file: QQFile,
        result: BackupTaskResult
    ) -> str:
        """下载单个文件"""
        try:
            # 获取下载URL
            url = await qq_file_repo.get_file_url(bot, file)
            
            # 下载文件
            await local_file_repo.download_file(
                file_path,
                url,
                timeout=ClientTimeout(total=backup_config.download_timeout)
            )
            
            return f"{file.folder_name}/{file.file_name}"
        
        except FileDownloadException as e:
            logger.warning(f"文件下载失败: {e}")
            return f"{file.folder_name}/{file.file_name}"
        except Exception as e:
            logger.error(f"文件下载异常: {e}", exc_info=True)
            return f"{file.folder_name}/{file.file_name}"
    
    @staticmethod
    def _get_file_key(file: QQFile) -> str:
        """获取文件唯一标识"""
        return f"{file.folder_name}/{file.file_name}"


# 全局服务实例
backup_service = BackupService()