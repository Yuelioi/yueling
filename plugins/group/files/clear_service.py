"""
清理和整理服务
"""
from pathlib import Path

from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot

from .exceptions import FolderOperationException
from .models_domain import ClearTaskResult, OrganizeTaskResult
from .qq_file_repo import qq_file_repo
from .task_executor import get_executor


class ClearService:
    """清理服务 - 删除指定扩展名的文件 只会删除根目录的"""
    
    async def execute_clear(
        self,
        bot: Bot,
        group_id: int,
        extensions: list[str]
    ) -> ClearTaskResult:
        """
        执行清理
        
        Args:
            bot: Bot实例
            group_id: 群号
            extensions: 要清理的文件扩展名列表
        
        Returns:
            ClearTaskResult: 清理结果
        """
        executor = get_executor(group_id)
        
        async def _clear():
            result = ClearTaskResult(target_extensions=extensions)
            
            try:
                # 获取QQ群中的所有文件
                logger.info(f"[{group_id}] 正在扫描群文件...")
                snapshot = await qq_file_repo.get_all_files_recursively(
                    bot=bot,
                    group_id=group_id,
                    include_root=True,
                    include_folders=False
                )
                
                # 筛选要删除的文件
                to_delete = [
                    f for f in snapshot.files
                    if self._should_delete(f.file_name, extensions)
                ]
                
                if not to_delete:
                    logger.info(f"[{group_id}] 没有发现需要清理的文件")
                    return result
                
                logger.info(f"[{group_id}] 发现 {len(to_delete)} 个待删除文件")
                
                # 删除文件
                for file in to_delete:
                    try:
                        await qq_file_repo.delete_file(bot, group_id, file)
                        result.success_count += 1
                    except Exception as e:
                        logger.warning(f"文件删除失败 {file.file_name}: {e}")
                        result.failed_files.append(file.file_name)
                
                return result
            
            except Exception as e:
                logger.error(f"[{group_id}] 清理异常: {e}", exc_info=True)
                result.error_message = str(e)
                return result
        
        return await executor.execute(_clear, "清理群文件")
    
    @staticmethod
    def _should_delete(filename: str, extensions: list[str]) -> bool:
        """检查文件是否应该被删除"""
        file_ext = Path(filename).suffix.lower().lstrip(".")
        return file_ext in extensions


class OrganizeService:
    """整理服务 - 将文件移动到指定文件夹 只能移动根目录的"""
    
    async def execute_organize(
        self,
        bot: Bot,
        group_id: int,
        target_folder: str,
        extensions: list[str]
    ) -> OrganizeTaskResult:
        """
        执行整理
        
        Args:
            bot: Bot实例
            group_id: 群号
            target_folder: 目标文件夹名称
            extensions: 要整理的文件扩展名列表
        
        Returns:
            OrganizeTaskResult: 整理结果
        """
        executor = get_executor(group_id)
        
        async def _organize():
            result = OrganizeTaskResult(
                target_folder=target_folder,
                target_extensions=extensions
            )
            
            try:
                # 获取QQ群中的所有文件
                logger.info(f"[{group_id}] 正在扫描群文件...")
                snapshot = await qq_file_repo.get_all_files_recursively(
                    bot=bot,
                    group_id=group_id,
                    include_root=True,
                    include_folders=False
                )
                
                # 筛选要整理的文件
                to_organize = [
                    f for f in snapshot.files
                    if self._should_organize(f.file_name, extensions)
                ]
                
                if not to_organize:
                    logger.info(f"[{group_id}] 没有发现需要整理的文件")
                    return result
                
                logger.info(f"[{group_id}] 发现 {len(to_organize)} 个待整理文件")
                
                # 查找或创建目标文件夹
                target_folder_obj = await qq_file_repo.find_folder(
                    bot, group_id, target_folder
                )
                
                if target_folder_obj is None:
                    logger.info(f"[{group_id}] 文件夹不存在，准备创建: {target_folder}")
                    target_folder_obj = await qq_file_repo.create_folder(
                        bot, group_id, target_folder
                    )
                    result.created_folder = True
                
                # 移动文件
                for file in to_organize:
                    try:
                        await qq_file_repo.move_file(
                            bot,
                            group_id,
                            file,
                            target_folder_obj.folder_id
                        )
                        result.success_count += 1
                    except Exception as e:
                        logger.warning(f"文件移动失败 {file.file_name}: {e}")
                        result.failed_files.append(file.file_name)
                
                return result
            
            except FolderOperationException as e:
                logger.error(f"[{group_id}] 文件夹操作失败: {e}")
                result.error_message = str(e)
                return result
            except Exception as e:
                logger.error(f"[{group_id}] 整理异常: {e}", exc_info=True)
                result.error_message = str(e)
                return result
        
        return await executor.execute(_organize, "整理群文件")
    
    @staticmethod
    def _should_organize(filename: str, extensions: list[str]) -> bool:
        """检查文件是否应该被整理"""
        file_ext = Path(filename).suffix.lower().lstrip(".")
        return file_ext in extensions


# 全局服务实例
clear_service = ClearService()
organize_service = OrganizeService()