import re

from nonebot import logger, on_message
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata

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


last_url = ""

link_analysis = on_message()


@link_analysis.handle()
async def link_handler(event: Event):
  global last_url
  url = event.get_plaintext()

  if url == last_url:
    return
  last_url = url

  url_handlers = [
    (r"(blog.csdn.net)", csdn),
    # (r"(music.163.com)", music163),
    # (r"(mp.weixin.qq)", wechat),
    (r"(zhuanlan.zhihu.com\/p)", zhihuzhuanlan),
    (r"(weibo.com)|(weibo.cn)", weibo),
    (r"(youtube.com)", youtube),
    (r"(x.com)", twitter),
    # (r"(github.com)", github),
    (
      r"(b23.tv)|(bili(22|23|33|2233).cn)|(.bilibili.com)|(^(av|cv)(\\d+))|(^BV([a-zA-Z0-9]{10})+)|(\\[\\[QQ小程序\\]哔哩哔哩\\])|(QQ小程序&amp;#93;哔哩哔哩)|(QQ小程序&#93;哔哩哔哩)",
      bilibili,
    ),
  ]

  for pattern, handler in url_handlers:
    match = re.search(pattern, url)
    if match:
      logger.info(f"链接解析:{url}")
      res = await handler(url)
      return await link_analysis.finish(res)
