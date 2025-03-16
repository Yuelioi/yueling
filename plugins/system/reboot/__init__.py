import asyncio
import subprocess

from nonebot import logger, on_command
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
  name="重启服务",
  description="重启服务",
  usage="""重启 + [服务名称:la/bot]""",
  extra={
    "group": "系统",
    "hidden": True,
  },
)
reboot = on_command("重启")


@reboot.handle()
async def rb(name: str):
  services = {"la": "la", "bot": "bot"}
  service = services.get(name, "bot")

  command = f"sudo supervisorctl restart {service}"

  try:
    await reboot.send(f"正在重启{service}服务...")
    await asyncio.to_thread(subprocess.run, command, shell=True, check=True)
  except subprocess.CalledProcessError as e:
    await reboot.send(f"重启{service}服务失败: {e}")
    logger.error(f"Error executing command: {e}")
  except Exception as e:
    await reboot.send(f"执行命令时发生错误: {e}")
    logger.error(f"Error executing command: {e}")
