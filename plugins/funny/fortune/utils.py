import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from plugins.funny.fortune.consts import (
  FORTUNE_CACHE,
  FORTUNE_COPYWRITING,
  FORTUNE_FONTS,
  FORTUNE_THEMES,
)


def get_copywriting() -> tuple[str, str]:
  """
  Read the copywriting.json, choice a luck with a random content
  """

  with open(FORTUNE_COPYWRITING, encoding="utf-8") as f:
    content = json.load(f).get("copywriting")

  luck = random.choice(content)

  title: str = luck.get("good-luck")
  text: str = random.choice(luck.get("content"))

  return title, text


def pick_image(theme: str) -> Path:
  # Each dir is a theme.
  themes: list[str] = [f.name for f in FORTUNE_THEMES.iterdir() if f.is_dir()]
  picked: str = random.choice(themes)

  # 指定主题
  for tm in themes:
    if theme == tm:
      picked = tm

  picked_theme: Path = FORTUNE_THEMES / picked

  # Each file is a posix path of images directory
  images_dir: list[Path] = [i for i in picked_theme.iterdir() if i.is_file()]

  return random.choice(images_dir)


def drawing(uid: str, now_time: str, theme: str) -> Path:
  # 1. Random choice a base image
  imgPath: Path = pick_image(theme)
  img: Image.Image = Image.open(imgPath)
  draw = ImageDraw.Draw(img)

  # 2. Random choice a luck text with title
  title, text = get_copywriting()

  # 3. Draw
  font_size = 45
  color = "#F5F5F5"
  image_font_center = [140, 99]
  fontPath = {
    "title": f"{FORTUNE_FONTS}/Mamelon.otf",
    "text": f"{FORTUNE_FONTS}/sakura.ttf",
  }
  ttfront = ImageFont.truetype(fontPath["title"], font_size)

  title_bbox = ttfront.getbbox(title)
  font_length = [title_bbox[2] - title_bbox[0], title_bbox[3] - title_bbox[1]]
  draw.text(
    (
      image_font_center[0] - font_length[0] / 2,
      image_font_center[1] - font_length[1] / 2,
    ),
    title,
    fill=color,
    font=ttfront,
  )

  # Text rendering
  font_size = 25
  color = "#323232"
  image_font_center = [140, 297]
  ttfront = ImageFont.truetype(fontPath["text"], font_size)
  slices, result = decrement(text)

  for i in range(slices):
    font_height: int = len(result[i]) * (font_size + 4)
    textVertical: str = "\n".join(result[i])
    x: int = int(image_font_center[0] + (slices - 2) * font_size / 2 + (slices - 1) * 4 - i * (font_size + 4))
    y: int = int(image_font_center[1] - font_height / 2)
    draw.text((x, y), textVertical, fill=color, font=ttfront)

  # Save

  outPath = FORTUNE_CACHE / f"{uid}-{now_time}.png"

  img.save(outPath)
  return outPath


def decrement(text: str) -> tuple[int, list[str]]:
  """
  Split the text, return the number of columns and text list
  TODO: Now, it ONLY fit with 2 columns of text
  """
  length: int = len(text)
  result: list[str] = []
  cardinality = 9
  if length > 4 * cardinality:
    raise Exception

  col_num: int = 1
  while length > cardinality:
    col_num += 1
    length -= cardinality

  # Optimize for two columns
  space = " "
  length = len(text)  # Value of length is changed!

  if col_num == 2:
    if length % 2 == 0:
      # even
      fillIn = space * int(9 - length / 2)
      return col_num, [text[: int(length / 2)] + fillIn, fillIn + text[int(length / 2) :]]
    else:
      # odd number
      fillIn = space * int(9 - (length + 1) / 2)
      return col_num, [text[: int((length + 1) / 2)] + fillIn, fillIn + space + text[int((length + 1) / 2) :]]

  for i in range(col_num):
    if i == col_num - 1 or col_num == 1:
      result.append(text[i * cardinality :])
    else:
      result.append(text[i * cardinality : (i + 1) * cardinality])

  return col_num, result
