from typing import Any

from arclet.alconna import AllParam
from nonebot_plugin_alconna import Alconna, Args, At, on_alconna

memo = on_alconna(Alconna(Any, Args["segs", AllParam]))


@memo.handle()
async def setu_h(segs: Any):
  for seg in segs:
    if isinstance(seg, At):
      at = seg.target
