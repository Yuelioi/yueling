import asyncio
import json

import socketio
from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata

from common.base.Depends import Arg

__plugin_meta__ = PluginMetadata(
  name="看电视",
  description="通过qq打开电脑链接(需要本地安装app)",
  usage="""看电视 + 链接""",
  extra={"group": "娱乐", "commands": ["看电视"]},
)


watch = on_command("看电视")


@watch.handle()
async def _watch_tv(event: GroupMessageEvent, link: str = Arg()):
  await watch.finish("维护中")
  sio = socketio.AsyncClient(logger=True, engineio_logger=True)

  serverURL = "http://127.0.0.1:12201"
  await sio.connect(serverURL, transports=["websocket"], socketio_path="socket.io")
  data = {"event_name": f"ev_{event.user_id}", "message": link}
  json_str = json.dumps(data)
  await sio.emit("message", json_str)

  await asyncio.sleep(5)
  await sio.disconnect()
