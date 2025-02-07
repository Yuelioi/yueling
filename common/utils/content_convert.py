from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from common.config import config


def text_to_image(text_list: list[str] | None, fontPath: str = "", background: str = ""):
  if not text_list:
    text_list = ["请勿传入空文字"]
  # 去掉\n

  text_list = [line for item in text_list for line in item.split("\n")]

  """将文字转为图片"""
  font_size = 24

  if not fontPath:
    fontPath = str(config.resource.fonts / "milai" / "Bold.ttf")

  if not background:
    background = str(config.resource.images / "background.png")

  font = ImageFont.truetype(fontPath, font_size)

  footage_clip_size = 60
  lines_space = 15
  line_padding_left_and_right = 60  # 文字距离最左边距离

  line_height = font_size + lines_space

  footage = Image.open(background)
  header = footage.crop(box=(0, 0, footage.width, footage_clip_size))
  footer = footage.crop(box=(0, footage.height - footage_clip_size, footage.width, footage.height))

  max_line_width = footage.width - line_padding_left_and_right * 2  # 自己减下边框值
  content = footage.crop(box=(0, footage_clip_size, footage.width, line_height + footage_clip_size))

  to_render_text_list = []
  for to_render_text in text_list:
    msg_size = get_msg_size(to_render_text, font)
    to_render_text_list.extend(split_content(to_render_text, msg_size, max_line_width))

  image_result = Image.new(
    "RGB",
    (footage.width, footage_clip_size * 2 + len(to_render_text_list) * line_height),
    color=255,
  )
  image_result.paste(im=header, box=(0, 0))

  for idx, text in enumerate(to_render_text_list):
    cache = content.copy()
    draw = ImageDraw.Draw(cache)
    draw.text(
      xy=(line_padding_left_and_right, 0),
      text=text,
      font=font,
      fill=(125, 97, 85),
    )
    image_result.paste(im=cache, box=(0, footage_clip_size + line_height * (idx)))

  image_result.paste(im=footer, box=(0, footage_clip_size + line_height * len(to_render_text_list)))

  byte_stream = BytesIO()
  image_result.save(byte_stream, format="JPEG")
  byte_stream.seek(0)

  return byte_stream


def get_msg_size(msg, font):
  """获取文字渲染后宽度"""
  size = []
  for t in msg:
    box = font.getbbox(t)
    size.append(box[2] - box[0])
  return size


def split_content(content, content_size_list, max_line_width):
  """清理文字, 转为合适长度的文字列表"""

  current_line_width = 0
  final_content = []
  last_index = 0

  for i in range(len(content)):
    if current_line_width + content_size_list[i] >= max_line_width:
      if i == len(content) - 1:
        # 正好最后一个字超了 直接加
        final_content.append(content[last_index:])
      else:
        final_content.append(content[last_index:i])
        last_index = i
        current_line_width = 0

    else:
      if i == len(content) - 1:
        final_content.append(content[last_index:])
      current_line_width += content_size_list[i]
  return final_content
