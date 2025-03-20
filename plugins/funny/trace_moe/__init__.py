from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.params import RawCommand
from nonebot.plugin import PluginMetadata

from common.base.Depends import Img
from common.utils import api, text_to_image
from plugins.funny.trace_moe.utils import trace_moe_util

__plugin_meta__ = PluginMetadata(
  name="图片识别",
  description="识别图片具体场景时间, 或者查询图片角色",
  usage="""场景识别/角色识别 + 1张图片""",
  extra={"group": "娱乐", "commands": ["场景识别", "角色识别"]},
)


trace = on_command("场景识别", aliases={"角色识别"})


@trace.handle()
async def image_trace(
  cmd=RawCommand(),
  img=Img(required=True),
):
  img_data = await api.fetch_image_from_url(img)

  if cmd == "场景识别":
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
    await trace.finish(MessageSegment.image(file=out_img))
  else:
    await trace.finish("接口维护中")
    # res = await trace_character_util(data=img_data.getvalue())
