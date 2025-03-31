import re

from nonebot.adapters import Bot, Event, Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.typing import T_State


def extract_qq_numbers(input_string: str):
  # 使用正则表达式查找连续的1到12位数字
  continuous_numbers = re.findall(r"\d{1,12}", input_string)
  number_list = [int(num) for num in continuous_numbers]
  return number_list


def get_command_args(state: T_State):
  if args := state.get("_prefix", {}).get("command_arg"):
    command: str = args.extract_plain_text()
    _args = command.strip().split()
    return _args

  return []


def Args(min_num: int = 1, max_num: int = 999):
  """提取多个参数 以空格或者回车分割"""

  async def dependency(matcher: Matcher, state: T_State):
    args = get_command_args(state)
    if len(args) > max_num or len(args) < min_num:
      await matcher.finish()
    return args

  return Depends(dependency)


def Arg(required=False):
  async def dependency(matcher: Matcher, state: T_State):
    args = get_command_args(state)
    if args:
      return args[0]

    if required:
      await matcher.finish()
    return ""

  return Depends(dependency)


async def get_at_users(bot: Bot, event: GroupMessageEvent, state: T_State):
  at_users: set[int] = set()

  # 添加数字型qq
  if args := state.get("_prefix", {}).get("command_arg"):
    args = args.extract_plain_text().strip().split()
    at_users.update(set(extract_qq_numbers(" ".join(args))))

  # 添加bot本体
  if event.is_tome():
    at_users.add(int(bot.self_id))

  # 过滤掉回复信息
  if event.reply:
    return []

  for seg in event.message:
    if seg.type == "at":
      qq = seg.data.get("qq")
      if qq and qq.isdigit():
        at_users.add(int(qq))
  return list(at_users)


def get_imgs(event: Event) -> list[str]:
  def extract_images(message: Message) -> list[str]:
    return [seg.data.get("url", seg.data.get("file", "")) for seg in message if seg.type == "image"]

  reply_images = []

  if isinstance(event, GroupMessageEvent):
    # 处理回复消息中的图片
    if event.reply:
      reply_images = extract_images(event.reply.message)

    # 处理当前消息中的图片
    current_images = extract_images(event.message)

  return reply_images + current_images


def Ats(min_num: int = 1, max_num: int = 99):
  async def dependeny(bot: Bot, event: GroupMessageEvent, matcher: Matcher, state: T_State):
    at_users = await get_at_users(bot, event, state)
    if len(at_users) > max_num or len(at_users) < min_num:
      await matcher.finish()
    return at_users

  return Depends(dependeny)


def At(required=False):
  async def dependency(bot: Bot, event: GroupMessageEvent, matcher: Matcher, state: T_State):
    at_users = await get_at_users(bot, event, state)
    if required:
      if not at_users:
        await matcher.finish("请@一个用户后再试")
      return next(iter(at_users))

    return next(iter(at_users)) if at_users else None

  return Depends(dependency)


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
