import asyncio
import json

import socketio
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot_plugin_alconna import on_alconna

from common.Alc.Alc import arg, pm, ptc

__plugin_meta__ = pm(
  name="看电视",
  description="通过qq打开电脑链接(需要本地安装app)",
  usage="""看电视 + 链接""",
  group="娱乐",
)

_watch = arg("看电视")
_watch.meta = ptc(__plugin_meta__)
watch = on_alconna(_watch)


@watch.handle()
async def _watch_tv(event: GroupMessageEvent, arg: str):
  await watch.finish("维护中")
  sio = socketio.AsyncClient(logger=True, engineio_logger=True)

  serverURL = "http://127.0.0.1:12201"
  await sio.connect(serverURL, transports=["websocket"], socketio_path="socket.io")
  data = {"event_name": f"ev_{event.user_id}", "message": arg}
  json_str = json.dumps(data)
  await sio.emit("message", json_str)

  await asyncio.sleep(5)
  await sio.disconnect()
