from io import BytesIO
from pathlib import Path

from nonebot.adapters.onebot.v11 import MessageSegment
from PIL import Image, ImageDraw, ImageFont

from common.config import config


def random_item(random_files=[]):
  if random_files:
    if pic := draw_grid(random_files):
      return MessageSegment.image(pic)


def draw_grid(
  files: list[Path],
  rows: int = 2,
  cols: int = 2,
  grid_width: int = 750,
  font_path=config.resource.fonts / "milai" / "Bold.ttf",
):
  """绘制可定制行列数的宫格图片，默认为九宫格"""

  # 根据提供的宽度和行列数计算每个格子的尺寸
  square_size = grid_width // cols
  grid_height = square_size * rows

  bg = Image.new("RGB", (grid_width, grid_height), 255)

  if font_path:
    font = ImageFont.truetype(str(font_path), 36)  # 调整字体大小以适应可能变化的格子大小
  else:
    font = None

  for idx, file in enumerate(files):
    if idx >= rows * cols:
      break

    img = Image.open(file)
    img_width, img_height = img.size
    min_side = min(img_width, img_height)

    left = (img_width - min_side) // 2
    top = (img_height - min_side) // 2
    right = left + min_side
    bottom = top + min_side

    cropped_img = img.crop((left, top, right, bottom))
    resized_img = cropped_img.resize((square_size, square_size))

    row = idx // cols
    col = idx % cols
    x1 = col * square_size
    y1 = row * square_size
    x2 = x1 + square_size
    y2 = y1 + square_size

    if font:
      draw = ImageDraw.Draw(resized_img)
      text_size = draw.textbbox((0, 0), text=file.stem, font=font)
      # 确保文本不会超出图像边界
      text_x = min(40, square_size - text_size[0])
      text_y = min(30, square_size - text_size[1])
      draw.text(
        (text_x, text_y),
        text=file.stem,
        font=font,
        fill=(250, 250, 250),
        stroke_fill=(100, 100, 100),
        stroke_width=3,
      )

    bg.paste(resized_img, (x1, y1, x2, y2))

  bytes_io = BytesIO()
  bg.save(bytes_io, format="PNG")
  bytes_io.seek(0)

  return bytes_io
