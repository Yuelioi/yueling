import os
import shutil
from pathlib import Path

from nonebot import on_command, on_fullmatch
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.permission import Permission
from nonebot.plugin import PluginMetadata

from common.base.Depends import Args
from common.base.Permission import Superuser_validate, User_admin_validate
from plugins.group.file.backup import bm
from plugins.group.file.models import LocalFile, QQFile
from plugins.group.file.utils import get_folder, get_root

WorkingMessage = "正在处理中/未知错误"


__plugin_meta__ = PluginMetadata(
  name="群文件管理",
  description="群文件管理, 部分需要管理权限",
  usage="""群文件 ~备份/~恢复/~清理/~整理 以及 本地文件清理""",
  extra={"group": "群管"},
)

backup = on_fullmatch("群文件备份", permission=Permission(Superuser_validate) | Permission(User_admin_validate))
recovery = on_fullmatch("群文件恢复", permission=Permission(Superuser_validate) | Permission(User_admin_validate))
organize = on_command("群文件整理", permission=Permission(Superuser_validate) | Permission(User_admin_validate))
clear = on_command("群文件清理", permission=Permission(Superuser_validate) | Permission(User_admin_validate))
local = on_fullmatch("本地文件清理", permission=Permission(Superuser_validate) | Permission(User_admin_validate))


async def run(event: GroupMessageEvent, matcher: Matcher, arg: str):
  if bm.event_info.is_processing:
    await matcher.finish(WorkingMessage)

  await matcher.send(arg)
  bm.event_info.start(bm.config.backup_dir / str(event.group_id))


@backup.handle()
async def _bk(
  bot: Bot,
  event: GroupMessageEvent,
  matcher: Matcher,
):
  await run(event=event, matcher=matcher, arg="备份中请稍后")

  try:
    bm.event_info.start(bm.config.backup_dir / str(event.group_id))
    await bm.collections(bot=bot, group_id=event.group_id, contain_root=False, contain_folder=True)

    # 创建本地文件夹
    for fd in bm.event_info.qqfolder_entries:
      (Path(bm.event_info.backup_directory) / fd["folder_name"]).mkdir(parents=True, exist_ok=True)

    localFile = {
      f"{Path(dirpath).name}_{filename}": os.path.join(dirpath, filename)
      for dirpath, _, filenames in os.walk(bm.event_info.backup_directory)
      for filename in filenames
    }

    # 计算需要下载的文件
    toDownloadFiles: list[QQFile] = [f for f in bm.event_info.qqfile_entries if f"{f.get('folder_name', '')}_{f['file_name']}" not in localFile]

    await bm.backup(bot, toDownloadFiles)
    bm.event_info.finish()
    msg = f"""-----备份群文件完成-----
      群文件数量:{len(bm.event_info.qqfile_entries)}
      需备份数量:{len(toDownloadFiles)}
      耗时: {bm.event_info.duration}秒
      {"" if not bm.event_info.failed_files else f"失败:{bm.event_info.failed_files}"}
      """.strip()
    await backup.send(msg)
  except Exception as e:
    await backup.send(f"备份过程中发生错误: {e}")
  finally:
    bm.event_info.next()


@recovery.handle()
async def _rc(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
  await run(event, matcher, "恢复中,请稍后…")
  await bm.collections(bot=bot, group_id=event.group_id, contain_root=True, contain_folder=True)
  try:
    # 计算需要上传的文件
    local_dir = bm.config.backup_dir / str(event.group_id)
    if not Path(local_dir).exists():
      await recovery.finish("本地暂无备份文件")
    webFiles = {f"{file.get('folder_name', '')}_{file['file_name']}": file for file in bm.event_info.qqfile_entries}
    webFolders = {qqfolder["folder_name"]: 1 for qqfolder in bm.event_info.qqfolder_entries}

    toUploadFiles: list[LocalFile] = []
    local_folder_names_set: set[str] = set()

    file_count = 0

    # 使用 os.walk 遍历本地目录
    for dirpath, _, filenames in os.walk(local_dir):
      for filename in filenames:
        file_path = os.path.join(dirpath, filename)
        relative_path = os.path.relpath(file_path, local_dir)
        folder_name = os.path.dirname(relative_path)
        file_count += 1
        # 检查文件是否已存在于云端
        if f"{folder_name}_{filename}" not in webFiles:
          toUploadFiles.append(LocalFile(file_path=file_path, file_name=filename, folder_name=folder_name))
          local_folder_names_set.add(folder_name)

    to_create_folder_names = [fd for fd in local_folder_names_set if fd not in webFolders and not fd == ""]
    await bm.recover(
      bot,
      group_id=event.group_id,
      toUploadFiles=toUploadFiles,
      need_create_folder_names=to_create_folder_names,
    )
    bm.event_info.finish()
    msg = f"""-----恢复群文件完成-----
      本地文件数量:{file_count}
      已上传数量:{len(toUploadFiles)}
      耗时: {bm.event_info.duration}秒
      {"" if not bm.event_info.failed_files else f"失败:{bm.event_info.failed_files}"}""".strip()
    await recovery.send(msg)
  except Exception as e:
    await recovery.send(f"恢复过程中发生错误: {e}")
  finally:
    bm.event_info.next()


@clear.handle()
async def _cl(bot: Bot, event: GroupMessageEvent, matcher: Matcher, args: list[str] = Args(0)):
  await run(event, matcher, "清理中,请稍后…")

  try:
    await bm.collections(bot=bot, group_id=event.group_id, contain_root=True, contain_folder=False, ignore_extensions=[])
    if not args:
      args = bm.config.ignore_extensions
    await bm.clear(bot, event.group_id, args)
    if bm.event_info.success_count > 0:
      bm.event_info.finish()
      await clear.send(f"清理完毕，共清理{bm.event_info.success_count}个文件, 耗时 {bm.event_info.duration:.2f} 秒")
    else:
      await clear.send("您的群文件很干净噢, 请再接再厉")
  except Exception as e:
    await clear.send(f"删除时发生错误：{e}")
  finally:
    bm.event_info.next()


@organize.handle()
async def _og(bot: Bot, event: GroupMessageEvent, matcher: Matcher, args: list[str] = Args(2)):
  await run(event, matcher, "整理中,请稍后…")

  folder = args[0]
  exts = args[1:]

  try:
    await bm.collections(bot=bot, group_id=event.group_id, contain_root=True, contain_folder=False, ignore_extensions=[])
    toOrganizeFiles: list[QQFile] = [f for f in bm.event_info.qqfile_entries if any(f["file_name"].endswith(ext) for ext in exts)]

    if len(toOrganizeFiles) == 0:
      await organize.send("群文件已经很整洁啦~不需要再整理了")
      return

    qqFolder = get_folder(bm.event_info.qqfolder_entries, folder)
    # 创建文件夹
    if qqFolder is None:
      await bot.create_group_file_folder(group_id=event.group_id, name=folder, parent_id="/")
      root = await get_root(bot=bot, group_id=event.group_id)
      qqFolder = get_folder(root["folders"], folder)

    if qqFolder is None:
      await organize.send("创建失败")
      return

    for file in toOrganizeFiles:
      await bot.call_api(
        "move_group_file",
        group_id=event.group_id,
        file_id=file["file_id"],
        parent_directory="/",
        target_directory=qqFolder["folder_id"],
      )
      bm.event_info.success_count += 1
    bm.event_info.finish()
    await organize.send(f"共收纳{bm.event_info.success_count}个文件, 耗时 {bm.event_info.duration:.2f} 秒")
  except Exception as e:
    await organize.send(f"整理时发生错误：{e}")
  finally:
    bm.event_info.next()


@local.handle()
async def _ll(
  matcher: Matcher,
  event: GroupMessageEvent,
):
  await run(event, matcher, "删除本地文件备份中,请稍后…")
  try:
    local_dir = bm.config.backup_dir / str(event.group_id)
    if local_dir.exists() and local_dir.is_dir():
      shutil.rmtree(local_dir)
    await local.send("清理完毕")
  except Exception as e:
    await local.send(f"删除本地备份时发生错误：{e}")
  finally:
    bm.event_info.next()
