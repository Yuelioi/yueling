import json

import aiofiles
from nonebot import logger
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.message import event_preprocessor
from nonebot_plugin_alconna import Arparma, on_alconna

from common.Alc.Alc import args, pm, ptc, register_handler
from common.config import config, gv

__plugin_meta__ = pm(
  name="关键词屏蔽",
  description="管理群组屏蔽关键词的插件。",
  usage="使用方法: 添加屏蔽[关键词] / 删除屏蔽[关键词] / 查看屏蔽",
  group="群管",
)


_keywords = args("添加屏蔽", required=False, meta=ptc(__plugin_meta__))
keywords = on_alconna(_keywords, aliases={"删除屏蔽", "查看屏蔽"})


@event_preprocessor
async def _(bot: Bot, event: GroupMessageEvent):
  if group := gv.group_ban_keywords.get(event.group_id, []):
    for key in group:
      if key in event.get_plaintext():
        await bot.delete_msg(message_id=event.message_id)
        break


async def save_keywords():
  try:
    async with aiofiles.open(config.data.group_ban_keywords, "w+", encoding="utf8") as f:
      await f.write(json.dumps(gv.group_ban_keywords, ensure_ascii=False))
  except Exception as e:
    logger.error(f"保存关键字时出错: {e}")
    await keywords.finish("保存关键字时出错，请稍后再试")


async def _kd(event: GroupMessageEvent, result: Arparma, args: list[str] = []):
  cmd = result.header_match.origin
  group_id = str(event.group_id)
  if cmd in ["添加屏蔽", "取消屏蔽"]:
    if not args:
      return "请指定关键词"

    if cmd == "添加屏蔽":
      group = gv.group_ban_keywords.setdefault(group_id, [])
      if not all(arg in group for arg in args):
        group.extend(arg for arg in args if arg not in group)
        await save_keywords()
      return "添加屏蔽成功"

    else:
      # 取消屏蔽
      group = gv.group_ban_keywords.get(group_id, [])
      if not all(arg not in group for arg in args):
        group[:] = [arg for arg in group if arg not in args]
        await save_keywords()
      return "取消屏蔽成功"

  else:
    group = gv.group_ban_keywords.get(str(event.group_id), [])
    if group:
      return "当前屏蔽词为: " + ", ".join(group)
    return "当前没有该屏蔽词喔"


register_handler(keywords, _kd)
