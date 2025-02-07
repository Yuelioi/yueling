from nonebot_plugin_alconna import Arparma, on_alconna

from common.Alc.Alc import fullmatch

trace = on_alconna(fullmatch("场景识别"), aliases={"角色识别"})


@trace.handle()
async def image_trace(result: Arparma):
  cmd = result.header_match.origin

  if cmd == "场景识别":
    return
  else:
    return
