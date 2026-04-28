from io import BytesIO
from pathlib import Path
from typing import Callable

from nonebot import logger
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.exception import FinishedException
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.typing import T_Handler


def auto_response_handler(dependency: T_Handler | None = None):
  async def handle(
    bot: Bot,
    matcher: Matcher,
    res=Depends(dependency),
  ):
    if res is None or not res:
      return
    try:
      if isinstance(res, (BytesIO, bytes, Path)):
        await matcher.finish(MessageSegment.image(file=res))
      elif isinstance(res, (Message, MessageSegment)):
        await matcher.finish(res)
      else:
        await matcher.finish(str(res))
    except FinishedException:
      return
    except Exception as e:
      logger.error(f"发送失败: {e}")

  return handle


def register_auto_handler(matcher: type[Matcher], func: Callable):
  matcher.append_handler(auto_response_handler(func))


# Deprecated aliases
res_handle = auto_response_handler
register_handler = register_auto_handler
