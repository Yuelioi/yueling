"""清理服务"""
from pathlib import Path

from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot

from .models_domain import ClearTaskResult
from .qq_file_repo import qq_file_repo
from .task_executor import get_executor


class ClearService:
    """清理服务 - 删除指定扩展名的根目录文件"""

    async def execute_clear(
        self,
        bot: Bot,
        group_id: int,
        extensions: list[str]
    ) -> ClearTaskResult:
        executor = get_executor(group_id)

        async def _clear():
            result = ClearTaskResult(target_extensions=extensions)

            try:
                logger.info(f"[{group_id}] 正在扫描群文件...")
                snapshot = await qq_file_repo.get_all_files_recursively(
                    bot=bot,
                    group_id=group_id,
                    include_root=True,
                    include_folders=False
                )

                to_delete = [
                    f for f in snapshot.files
                    if self._should_delete(f.file_name, extensions)
                ]

                if not to_delete:
                    logger.info(f"[{group_id}] 没有发现需要清理的文件")
                    return result

                logger.info(f"[{group_id}] 发现 {len(to_delete)} 个待删除文件")

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
        file_ext = Path(filename).suffix.lower().lstrip(".")
        return file_ext in extensions


clear_service = ClearService()
