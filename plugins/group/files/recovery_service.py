"""
恢复服务业务逻辑
"""
from pathlib import Path

from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot

from .config import backup_config
from .exceptions import BackupNotFoundError, FileUploadException
from .local_file_repo import local_file_repo
from .models_domain import LocalFile, RecoveryTaskResult
from .qq_file_repo import qq_file_repo
from .task_executor import get_executor


class RecoveryService:
    """恢复服务"""
    
    async def execute_recovery(self, bot: Bot, group_id: int) -> RecoveryTaskResult:
        """
        执行群文件恢复
        
        Args:
            bot: Bot实例
            group_id: 群号
        
        Returns:
            RecoveryTaskResult: 恢复结果
        """
        executor = get_executor(group_id)
        
        async def _recovery():
            result = RecoveryTaskResult()
            
            try:
                # 检查本地备份是否存在
                backup_dir = backup_config.get_backup_directory(group_id)
                if not backup_dir.exists():
                    raise BackupNotFoundError(f"群 {group_id} 的本地备份不存在")
                
                # 获取本地备份文件
                logger.info(f"[{group_id}] 正在扫描本地备份...")
                local_files = local_file_repo.get_local_files(backup_dir)
                result.total_local_files = len(local_files)
                logger.info(f"[{group_id}] 发现 {result.total_local_files} 个本地备份文件")
                
                # 获取QQ群中已有的文件
                logger.info(f"[{group_id}] 正在扫描群文件...")
                snapshot = await qq_file_repo.get_all_files_recursively(
                    bot=bot,
                    group_id=group_id,
                    include_root=True,
                    include_folders=True
                )
                
                # 构建云端文件映射
                web_files = {
                    self._get_file_key(f): f
                    for f in snapshot.files
                }
                web_folders = {f.folder_name: f.folder_id for f in snapshot.folders}
                
                # 计算需要上传的文件和需要创建的文件夹
                to_upload = []
                to_create_folders = set()
                
                for file_key, file_path in local_files.items():
                    if file_key not in web_files:
                        folder_name = str(Path(file_key).parent)
                        if folder_name == ".":
                            folder_name = ""
                        
                        to_upload.append(
                            LocalFile(
                                file_path=file_path,
                                file_name=Path(file_path).name,
                                folder_name=folder_name
                            )
                        )
                        
                        if folder_name and folder_name not in web_folders:
                            to_create_folders.add(folder_name)
                
                result.upload_count = len(to_upload)
                logger.info(f"[{group_id}] 需要上传 {result.upload_count} 个文件")
                
                if to_create_folders:
                    logger.info(f"[{group_id}] 需要创建 {len(to_create_folders)} 个文件夹")
                    await self._create_folders(bot, group_id, list(to_create_folders), web_folders, result)
                
                # 执行上传
                if to_upload:
                    await self._upload_files(bot, group_id, to_upload, web_folders, result)
                
                return result
            
            except BackupNotFoundError as e:
                logger.error(f"[{group_id}] 恢复失败: {e}")
                result.error_message = str(e)
                return result
            except Exception as e:
                logger.error(f"[{group_id}] 恢复异常: {e}", exc_info=True)
                result.error_message = str(e)
                return result
        
        return await executor.execute(_recovery, "恢复群文件")
    
    async def _create_folders(
        self,
        bot: Bot,
        group_id: int,
        folder_names: list[str],
        existing_folders: dict[str, str],
        result: RecoveryTaskResult
    ) -> None:
        """创建不存在的文件夹"""
        for folder_name in folder_names:
            try:
                await qq_file_repo.create_folder(bot, group_id, folder_name)
                existing_folders[folder_name] = folder_name  # 简化处理
                result.created_folders.append(folder_name)
                logger.info(f"[{group_id}] 文件夹创建成功: {folder_name}")
            except Exception as e:
                logger.error(f"[{group_id}] 文件夹创建失败 {folder_name}: {e}")
    
    async def _upload_files(
        self,
        bot: Bot,
        group_id: int,
        files: list[LocalFile],
        web_folders: dict[str, str],
        result: RecoveryTaskResult
    ) -> None:
        """批量上传文件"""
        executor = get_executor(group_id)
        
        # 生成上传任务
        upload_tasks = []
        for file in files:
            upload_tasks.append(
                self._upload_single_file(bot, group_id, file, web_folders, result)
            )
        
        # 执行并发上传
        successes, failures = await executor.execute_with_concurrency(
            upload_tasks,
            max_workers=backup_config.max_concurrent_uploads,
            task_name="文件上传"
        )
        
        result.success_count = len(successes)
        result.failed_files = failures
    
    async def _upload_single_file(
        self,
        bot: Bot,
        group_id: int,
        file: LocalFile,
        web_folders: dict[str, str],
        result: RecoveryTaskResult
    ) -> str:
        """上传单个文件"""
        try:
            folder_id = web_folders.get(file.folder_name) if file.folder_name else None
            
            await qq_file_repo.upload_file(
                bot,
                group_id,
                str(file.file_path.resolve()),
                file.file_name,
                folder_id
            )
            
            return f"{file.folder_name}/{file.file_name}" if file.folder_name else file.file_name
        
        except FileUploadException as e:
            logger.warning(f"文件上传失败: {e}")
            return f"{file.folder_name}/{file.file_name}" if file.folder_name else file.file_name
        except Exception as e:
            logger.error(f"文件上传异常: {e}", exc_info=True)
            return f"{file.folder_name}/{file.file_name}" if file.folder_name else file.file_name
    
    @staticmethod
    def _get_file_key(file) -> str:
        """获取文件唯一标识"""
        return f"{file.folder_name}/{file.file_name}" if file.folder_name else file.file_name


# 全局服务实例
recovery_service = RecoveryService()