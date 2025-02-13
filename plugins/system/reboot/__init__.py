import asyncio
import subprocess

from nonebot import logger
from nonebot_plugin_alconna import Alconna, Args, on_alconna
from nonebot_plugin_alconna.builtins.extensions.reply import ReplyMergeExtension

from common.Alc.Alc import pm, ptc
from common.Alc.Permission import Superuser_Checker

__plugin_meta__ = pm(
  name="重启服务",
  description="重启服务",
  usage="""重启 + [服务名称:la/bot]""",
  group="系统",
  hidden=True,
)
_reboot = Alconna("重启", Args["name", str])

_reboot.meta = ptc(__plugin_meta__)
reboot = on_alconna(_reboot, extensions=[ReplyMergeExtension])


@reboot.assign(path="$main", additional=Superuser_Checker)
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
