"""
QQ文件数据访问层
"""
from collections import deque
from typing import Optional, Tuple

from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot

from .exceptions import FolderOperationException
from .models_domain import QQFile, QQFolder, GroupFileSnapshot


class QQFileRepository:
    """QQ文件操作仓储"""
    
    def __init__(self):
        self._snapshot_cache: dict[int, GroupFileSnapshot] = {}
    
    async def get_root_files(self, bot: Bot, group_id: int) -> GroupFileSnapshot:
        """
        获取群根目录文件和文件夹
        
        Returns:
            GroupFileSnapshot: 包含文件和文件夹的快照
        """
        try:
            root_data = await bot.get_group_root_files(group_id=group_id,file_count= 9999)
          
            return GroupFileSnapshot(
                group_id=group_id,
                files=[QQFile(**f) for f in root_data.get("files", [])],
                folders=[QQFolder(**f) for f in root_data.get("folders", [])],
            )
        except Exception as e:
            logger.error(f"获取群 {group_id} 根目录失败: {e}")
            raise
    
    async def get_folder_files(
        self,
        bot: Bot,
        group_id: int,
        folder_id: str,
        folder_name: str
    ) -> Tuple[list[QQFile], list[QQFolder]]:
        """
        获取指定文件夹的文件和子文件夹
        
        Args:
            bot: Bot实例
            group_id: 群号
            folder_id: 文件夹ID
            folder_name: 文件夹名称
        
        Returns:
            (文件列表, 文件夹列表)
        """
        try:
            folder_data = await bot.get_group_files_by_folder(
                group_id=group_id,
                folder_id=folder_id,
                file_count= 9999
            )
            
            files = [
                QQFile(**f, folder_name=folder_name)
                for f in folder_data.get("files", [])
            ]
            
            folders = [
                QQFolder(**f)
                for f in folder_data.get("folders", [])
            ]

            
            return files, folders
        except Exception as e:
            logger.error(f"获取文件夹 {folder_name} 内容失败: {e}")
            raise
    
    async def get_all_files_recursively(
        self,
        bot: Bot,
        group_id: int,
        include_root: bool = True,
        include_folders: bool = True
    ) -> GroupFileSnapshot:
        """
        递归获取所有文件和文件夹
        
        Args:
            bot: Bot实例
            group_id: 群号
            include_root: 是否包含根目录文件
            include_folders: 是否包含子文件夹中的文件
        
        Returns:
            GroupFileSnapshot: 文件快照
        """
        all_files: list[QQFile] = []
        all_folders: list[QQFolder] = []
        
        # 获取根目录
        root_snapshot = await self.get_root_files(bot, group_id)
        all_folders.extend(root_snapshot.folders)
        
        if include_root:
            all_files.extend(root_snapshot.files)
        
        # 递归获取所有文件夹中的文件
        if include_folders:
            queue = deque(root_snapshot.folders)
            while queue:
                folder = queue.popleft()
                try:
                    files, subfolders = await self.get_folder_files(
                        bot, group_id, folder.folder_id, folder.folder_name
                    )
                    all_files.extend(files)
                    all_folders.extend(subfolders)
                    queue.extend(subfolders)
                except Exception as e:
                    logger.warning(f"获取文件夹 {folder.folder_name} 失败，跳过: {e}")
                    continue
        
        return GroupFileSnapshot(
            group_id=group_id,
            files=all_files,
            folders=all_folders
        )
    
    async def get_file_url(self, bot: Bot, file: QQFile) -> str:
        """获取文件下载URL"""
        try:
            file_info = await bot.get_group_file_url(
                group_id=file.group_id,
                file_id=file.file_id,
                busid=file.busid
            )
            return file_info["url"]
        except Exception as e:
            logger.error(f"获取文件 {file.file_name} 的URL失败: {e}")
            raise
    
    async def create_folder(
        self,
        bot: Bot,
        group_id: int,
        folder_name: str,
        parent_folder_id: str = "/"
    ) -> QQFolder:
        """
        创建文件夹
        
        Returns:
            创建的文件夹对象
        """
        try:
            await bot.create_group_file_folder(
                group_id=group_id,
                name=folder_name,
                parent_id=parent_folder_id
            )
            logger.info(f"文件夹 {folder_name} 创建成功")
            
            # 获取新创建的文件夹信息
            root = await self.get_root_files(bot, group_id)
            for folder in root.folders:
                if folder.folder_name == folder_name:
                    return folder
            
            raise FolderOperationException(
                folder_name, "create", "创建后未找到新文件夹"
            )
        except Exception as e:
            raise FolderOperationException(folder_name, "create", str(e))
    
    async def find_folder(
        self,
        bot: Bot,
        group_id: int,
        folder_name: str
    ) -> Optional[QQFolder]:
        """查找指定名称的文件夹"""
        root = await self.get_root_files(bot, group_id)
        for folder in root.folders:
            if folder.folder_name == folder_name:
                return folder
        return None
    
    async def delete_file(
        self,
        bot: Bot,
        group_id: int,
        file: QQFile
    ) -> None:
        """删除文件"""
        try:
            await bot.call_api(
                "delete_group_file",
                group_id=group_id,
                file_id=file.file_id,
                busid=file.busid
            )
            logger.debug(f"文件 {file.file_name} 删除成功")
        except Exception as e:
            logger.error(f"删除文件 {file.file_name} 失败: {e}")
            raise
    
    async def move_file(
        self,
        bot: Bot,
        group_id: int,
        file: QQFile,
        target_folder_id: str
    ) -> None:
        """移动文件到目标文件夹"""
        try:
            await bot.call_api(
                "move_group_file",
                group_id=group_id,
                file_id=file.file_id,
                current_parent_directory="/",
                target_parent_directory=target_folder_id
            )
            logger.debug(f"文件 {file.file_name} 移动成功")
        except Exception as e:
            logger.error(f"移动文件 {file.file_name} 失败: {e}")
            raise
    
    async def upload_file(
        self,
        bot: Bot,
        group_id: int,
        file_path: str,
        file_name: str,
        folder_id: Optional[str] = None
    ) -> None:
        """上传文件到群"""
        try:
            await bot.upload_group_file(
                group_id=group_id,
                file=file_path,
                name=file_name,
                folder=folder_id
            )
            logger.debug(f"文件 {file_name} 上传成功")
        except Exception as e:
            logger.error(f"上传文件 {file_name} 失败: {e}")
            raise


# 全局仓储实例
qq_file_repo = QQFileRepository()