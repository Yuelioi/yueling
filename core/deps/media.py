"""图片提取"""

from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import Depends

from core.context import extract_images


def get_imgs(event: Event) -> list[str]:
  if isinstance(event, GroupMessageEvent):
    return extract_images(event)
  return []


def Imgs(min_num: int = 1, max_num: int = 99):
  async def dependency(event: Event, matcher: Matcher):
    imgs = get_imgs(event)
    if len(imgs) > max_num or len(imgs) < min_num:
      await matcher.finish()
    return imgs

  return Depends(dependency)


def Img(required=False):
  async def dependency(event: Event, matcher: Matcher):
    imgs = get_imgs(event)
    if not imgs and required:
      await matcher.finish("请提供一张图片/艾特一个群友")
    if not imgs:
      return ""
    return next(iter(imgs))

  return Depends(dependency)
