import re

from nonebot import logger, on_message
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata
from nonebot.rule import Rule

from plugins.tools.link_analysis.behance import behance
from plugins.tools.link_analysis.bilibili import bilibili
from plugins.tools.link_analysis.csdn import csdn
from plugins.tools.link_analysis.twitter import twitter
from plugins.tools.link_analysis.weibo import weibo
from plugins.tools.link_analysis.ytb import youtube
from plugins.tools.link_analysis.zhihu import zhihuzhuanlan

__plugin_meta__ = PluginMetadata(
  name="链接解析",
  description="",
  usage="被动技能",
  extra={
    "group": "工具",
  },
)

URL_PATTERNS = [
  (r"(blog.csdn.net)", csdn),
  (r"(zhuanlan.zhihu.com\/p)", zhihuzhuanlan),
  (r"(weibo.com)|(weibo.cn)", weibo),
  (r"(youtube.com)", youtube),
  (r"(x.com)", twitter),
  (r"(behance.net/gallery/.+)", behance),
  (
    r"(b23.tv)|(bili(22|23|33|2233).cn)|(.bilibili.com)|(^(av|cv)(\\d+))|(^BV([a-zA-Z0-9]{10})+)|(\\[\\[QQ小程序\\]哔哩哔哩\\])|(QQ小程序&amp;#93;哔哩哔哩)|(QQ小程序&#93;哔哩哔哩)",
    bilibili,
  ),
]


class _State:
  last_url: str = ""


_state = _State()


def _has_url(event: GroupMessageEvent) -> bool:
  text = event.get_plaintext()
  return any(re.search(pat, text) for pat, _ in URL_PATTERNS)


link_analysis = on_message(rule=Rule(_has_url))


@link_analysis.handle()
async def link_handler(event: GroupMessageEvent, bot: Bot):
  url = event.get_plaintext()

  if url == _state.last_url:
    return
  _state.last_url = url

  for pattern, handler in URL_PATTERNS:
    if re.search(pattern, url):
      logger.info(f"链接解析:{url}")
      if "x.com" in pattern:
        res = await handler(bot, event, url)
      else:
        res = await handler(url)
      return await link_analysis.finish(res)
