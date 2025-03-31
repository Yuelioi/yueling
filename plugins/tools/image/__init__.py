import random
from io import BytesIO

from nonebot import on_command
from nonebot.plugin import PluginMetadata
from PIL import Image

from common.base.Depends import Img
from common.base.Handle import register_handler
from common.utils import api

__plugin_meta__ = PluginMetadata(
  name="图片处理",
  description="",
  usage="""""",
  extra={"group": "工具", "comands": ["抽帧"]},
)
gif_random_frame = on_command("随机截图")


async def gif_random_handler(img: str = Img(required=True)):
  """随机截取GIF的某一帧"""
  try:
    # 获取图片数据
    data = await api.fetch_image_from_url_ssl(img)
    gif = Image.open(data)

    # 验证是否为GIF格式
    if gif.format != "GIF":
      return "只支持GIF格式图片"

    # 获取所有帧
    total_frames = getattr(gif, "n_frames", 1)

    # 随机选择帧索引
    target_frame = random.randint(0, total_frames - 1)

    # 跳转到指定帧
    gif.seek(target_frame)

    # 转换格式输出
    output = BytesIO()
    gif.save(output, format="PNG")

    # 返回图片
    return output

  except Exception as e:
    return "处理GIF时发生错误"


register_handler(gif_random_frame, gif_random_handler)
