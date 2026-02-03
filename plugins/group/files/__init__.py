"""
命令处理器 - 处理用户命令和消息交互
"""
from typing import List, Optional

from nonebot import logger, on_command, on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.permission import Permission
from nonebot.plugin import PluginMetadata

from common.base.Depends import Args
from common.base.Permission import Superuser_validate, User_admin_validate

from .backup_service import backup_service
from .clear_service import clear_service
from .config import backup_config
from .exceptions import BackupStateException
from .local_file_repo import local_file_repo
from .models_domain import TaskResult
from .organize_service import organize_service
from .recovery_service import recovery_service
from .task_executor import get_executor

from .query_service import query_service

__plugin_meta__ = PluginMetadata(
    name="群文件管理",
    description="群文件管理，部分需要管理权限",
    usage="群文件 备份/恢复/清理/整理 以及 本地文件清理",
    extra={
        "group": "群管",
        "commands": ["群文件备份", "群文件恢复", "群文件清理", "群文件整理", "本地文件清理","群文件查询",]
    },
)

# 定义命令处理器
backup_cmd = on_fullmatch(
    "群文件备份",
    permission=Permission(Superuser_validate) | Permission(User_admin_validate)
)
recovery_cmd = on_fullmatch(
    "群文件恢复",
    permission=Permission(Superuser_validate) | Permission(User_admin_validate)
)
organize_cmd = on_command(
    "群文件整理",
    permission=Permission(Superuser_validate) | Permission(User_admin_validate)
)
clear_cmd = on_command(
    "群文件清理",
    permission=Permission(Superuser_validate) | Permission(User_admin_validate)
)
local_cmd = on_fullmatch(
    "本地文件清理",
    permission=Permission(Superuser_validate) | Permission(User_admin_validate)
)
query_cmd = on_command(
    "群文件查询",
)



class CommandHandler:
    """命令处理基类"""
    
    @staticmethod
    async def check_processing(group_id: int, matcher: Matcher) -> bool:
        """检查是否已有任务在执行"""
        executor = get_executor(group_id)
        if executor.is_processing:
            await matcher.finish("已有任务在执行中，请稍候...")
            return False
        return True
    
    @staticmethod
    async def send_progress(matcher: Matcher, message: str) -> None:
        """发送进度消息"""
        await matcher.send(message)
    
    @staticmethod
    async def send_result(
        matcher: Matcher,
        task_name: str,
        result: TaskResult,
        detail_template: str = ""
    ) -> None:
        """发送任务结果"""
        if result.error_message:
            await matcher.send(f"❌ {task_name}失败: {result.error_message}")
            return
        
        # 构建基本消息
        base_msg = f"✅ {task_name}完成\n耗时: {result.duration}秒"
        
        if result.failed_files:
            base_msg += f"\n⚠️ 失败文件数: {len(result.failed_files)}"
            if len(result.failed_files) <= 5:
                base_msg += f"\n失败文件:\n" + "\n".join(result.failed_files)
        
        if detail_template:
            base_msg += f"\n{detail_template}"
        
        await matcher.send(base_msg)


@backup_cmd.handle()
async def handle_backup(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    """处理备份命令"""
    if not await CommandHandler.check_processing(event.group_id, matcher):
        return
    

    await CommandHandler.send_progress(matcher, "正在备份群文件，请稍候...")

    
    result = await backup_service.execute_backup(bot, event.group_id)
    
    detail = f"成功: {result.success_count}/{result.download_count}"
    await CommandHandler.send_result(matcher, "备份", result, detail)


@recovery_cmd.handle()
async def handle_recovery(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    """处理恢复命令"""
    if not await CommandHandler.check_processing(event.group_id, matcher):
        return
    
    
    result = await recovery_service.execute_recovery(bot, event.group_id)
    
    detail = f"成功: {result.success_count}/{result.upload_count}"
    if result.created_folders:
        detail += f"\n创建文件夹: {', '.join(result.created_folders)}"
    
    await CommandHandler.send_result(matcher, "恢复", result, detail)


@clear_cmd.handle()
async def handle_clear(
    bot: Bot,
    event: GroupMessageEvent,
    matcher: Matcher,
    args: List[str] = Args(0)
):
    """处理清理命令"""
    if not await CommandHandler.check_processing(event.group_id, matcher):
        return
    
    # 使用指定的扩展名或默认扩展名
    extensions = args if args else backup_config.ignore_extensions
    

    
    result = await clear_service.execute_clear(bot, event.group_id, extensions)
    
    await CommandHandler.send_result(matcher, "清理", result)


@organize_cmd.handle()
async def handle_organize(
    bot: Bot,
    event: GroupMessageEvent,
    matcher: Matcher,
    args: List[str] = Args(2)
):
    """处理整理命令"""
    if not await CommandHandler.check_processing(event.group_id, matcher):
        return
    
    if len(args) < 2:
        await matcher.finish("用法: 群文件整理 <文件夹名> <扩展名1> [扩展名2]...")
        return
    
    folder_name = args[0]
    extensions = args[1:]
    

    
    result = await organize_service.execute_organize(
        bot,
        event.group_id,
        folder_name,
        extensions
    )
    
    detail = f"文件夹: {result.target_folder}"
    if result.created_folder:
        detail += " (新建)"
    
    await CommandHandler.send_result(matcher, "整理", result, detail)


@local_cmd.handle()
async def handle_local_cleanup(
    bot: Bot,
    event: GroupMessageEvent,
    matcher: Matcher
):
    """处理本地文件清理命令"""
    if not await CommandHandler.check_processing(event.group_id, matcher):
        return
    

    
    try:
        backup_dir = backup_config.get_backup_directory(event.group_id)
        await local_file_repo.delete_directory(backup_dir)
        await CommandHandler.send_result(
            matcher,
            "本地文件清理",
            TaskResult(success_count=1)
        )
    except Exception as e:
        logger.error(f"本地文件清理失败: {e}", exc_info=True)
        await matcher.send(f"❌ 清理失败: {e}")


@query_cmd.handle()
async def handle_query(
    bot: Bot,
    event: GroupMessageEvent,
    matcher: Matcher,
    args: List[str] = Args(1)
):
    """处理群文件查询命令"""
    if not await CommandHandler.check_processing(event.group_id, matcher):
        return

    if not args:
        await matcher.finish("用法: 群文件查询 <关键词>")
        return

    keyword = args[0]


    result = await query_service.execute_query(
        bot,
        event.group_id,
        keyword
    )

    if not result.files:
        await matcher.send("未找到匹配的文件")
        return

    msg_lines = ["查询结果（最多显示5个）:"]
    for idx, f in enumerate(result.files, start=1):
        size_mb = f.size / 1024 / 1024
        msg_lines.append(
            f"{idx}. {f.file_name}\n"
            f"   文件夹: {f.folder}\n"
            f"   大小: {size_mb:.2f} MB"
        )

    await matcher.send("\n".join(msg_lines))
