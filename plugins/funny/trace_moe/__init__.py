from nonebot_plugin_alconna import Arparma, Image, UniMessage, on_alconna
from nonebot_plugin_alconna.builtins.extensions.reply import ReplyMergeExtension

from common.Alc.Alc import multi_args, pm, ptc
from common.utils import api, text_to_image
from plugins.funny.trace_moe.utils import trace_moe_util

__plugin_meta__ = pm(
  name="图片识别",
  description="识别图片具体场景时间, 或者查询图片角色",
  usage="""场景识别/角色识别 + 1张图片""",
  group="娱乐",
)

_trace = multi_args("场景识别", ("img", Image))
_trace.meta = ptc(__plugin_meta__)
trace = on_alconna(_trace, aliases={"角色识别"}, extensions=[ReplyMergeExtension])


@trace.handle()
async def image_trace(
  result: Arparma,
  img: Image,
):
  if not img.url:
    return

  img_data = await api.fetch_image_from_url(img.url)
  arg = result.header_match.origin  # .result是主命令 origin是当前命令

  if arg == "场景识别":
    res = await trace_moe_util(data=img_data.getvalue())

    if not res:
      return "获取数据失败"

    res = res.get("result")

    output = []

    for (
      index,
      item,
    ) in enumerate(res):
      # similarity = item["similarity"]
      _from = item["from"]
      title = item["anilist"]["title"]["native"]
      episode = item["episode"]
      # filename = item["filename"]

      output.extend(
        [
          f"标题: {title}",
          f"集数: {episode if episode else '无'} | 时间点: {_from}",
          # f"文件名: {filename}",
          # f"相似度: {similarity}",
          "---------------------------",
        ]
      )

    out_img = text_to_image(output)
    await trace.finish(UniMessage.image(raw=out_img))
  else:
    await trace.finish("接口维护中")
    # res = await trace_character_util(data=img_data.getvalue())
