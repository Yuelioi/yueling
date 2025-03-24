import base64
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path
from typing import Optional

import cloudscraper
import requests
from bs4 import BeautifulSoup
from natsort import natsorted
from nonebot import logger, on_command
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.plugin import PluginMetadata
from PIL import Image
from tenacity import RetryError, retry, stop_after_attempt, wait_fixed
from urllib3.util import Retry

from common import config
from common.base.Depends import Args

__plugin_meta__ = PluginMetadata(
  name="JM",
  description="JM",
  usage="""jm id [章节号]""",
  extra={
    "group": "娱乐",
    "commands": ["jm", "JM"],
  },
)


# 全局配置
BASE_URL = "https://18comic.vip/"
PROXIES = {
  "http": "http://127.0.0.1:10808",
  "https": "http://127.0.0.1:10808",
}
HEADERS = {
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
  "Accept-Language": "zh-CN,zh;q=0.9",
  "Referer": BASE_URL,
}

MAX_WORKERS = 5  # 并发线程数
WAIT_TIME = 1  # 重试等待秒数
RETRY_TIMES = 6  # 重试次数
RETRY_STRATEGY = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["HEAD", "GET", "OPTIONS"])


jm = on_command("jm", aliases={"JM", "Jm"})

save_dir = config.config.resource.images / "jm"


@jm.handle()
async def handle(bot: Bot, event: GroupMessageEvent, args: list[str] = Args(1, 2)):
  """主程序"""
  if not str(event.group_id).startswith("827264"):
    return

  session = create_session()
  book_id = args[0]
  charpter_id = 1

  if len(args) == 2:
    charpter_id = abs(int(args[1]))

  tmp_folder = save_dir / book_id
  tmp_folder.mkdir(parents=True, exist_ok=True)

  pdf_file = tmp_folder / (book_id + f"_{charpter_id}.pdf")

  if pdf_file.exists():
    await bot.call_api("upload_group_file", group_id=event.group_id, file=str(pdf_file.resolve()), name=book_id + ".pdf")
    return

  # 获取章节
  logger.info("正在解析章节...")
  chapters = parse_book(session, book_id)
  if not chapters:
    logger.error("未找到任何章节")
    await jm.finish("网络错误(请稍后重试)/未找到任何章节")

  # 多线程下载
  logger.info("开始下载图片...")

  with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = []
    if charpter_id > len(chapters):
      await jm.finish(f"最多只有{len(chapters)}章节喔")

    await jm.send(f"下载中, 请稍后{charpter_id}/{len(chapters)}")
    for chapter in chapters[charpter_id - 1 : charpter_id]:
      chapter_url = chapter.lstrip("/")
      logger.info(chapter_url)
      img_urls = get_img_urls(session, chapter_url)
      if not img_urls:
        continue

      for idx, img_url in enumerate(img_urls):
        filename = f"{chapter_url.replace('photo/', '')}_{idx + 1:03d}.webp"

        save_path = os.path.join(tmp_folder, filename)
        if os.path.exists(save_path):
          continue

        futures.append(executor.submit(download_image, session, img_url, save_path))

    # 显示进度
    for future in as_completed(futures):
      try:
        success = future.result()
        if success:
          logger.debug("下载成功")
      except Exception as e:
        await jm.finish(f"下载出错: {e}")
        logger.error(f"下载出错: {e}")

  # 生成PDF
  logger.info("正在生成PDF...")

  try:
    convert_images_to_pdf(tmp_folder, pdf_file)

    logger.info("处理完成")
  except Exception as e:
    logger.error(f"生成PDF失败: {e}")
  finally:
    if pdf_file.exists():
      await bot.call_api("upload_group_file", group_id=event.group_id, file=str(pdf_file.resolve()), name=book_id + ".pdf")
    else:
      await jm.finish("生成PDF失败")


def create_session() -> requests.Session:
  """创建Session"""
  scraper = cloudscraper.create_scraper()
  scraper.proxies = PROXIES
  scraper.headers.update(HEADERS)
  return scraper


@retry(stop=stop_after_attempt(RETRY_TIMES), wait=wait_fixed(WAIT_TIME))
def fetch_with_retry(session: requests.Session, url: str) -> requests.Response:
  """带重试机制的请求函数"""
  try:
    response = session.get(url, timeout=10)
    response.raise_for_status()
    return response
  except requests.exceptions.HTTPError as e:
    logger.error(f"HTTPError during fetching {url}: {e}")
    raise
  except requests.RequestException as e:
    logger.error(f"RequestException during fetching {url}: {e}")
    raise


def parse_book(session: requests.Session, book_id: str) -> list[str]:
  """解析漫画书章节链接"""
  url = f"{BASE_URL}album/{book_id}/"
  try:
    response = fetch_with_retry(session, url)
    response.raise_for_status()
  except requests.exceptions.HTTPError as e:
    logger.error(f"{url} 请求章节失败: {e}")
    return []
  except RetryError as e:
    logger.error(f"重试失败: {e.last_attempt.exception()}")
    return []

  soup = BeautifulSoup(response.text, "lxml")
  episode_links = soup.select("#episode-block > div > div > ul > a[href]")
  if not episode_links:
    return [f"photo/{book_id}"]
  return [str(a["href"]) for a in episode_links if a.has_attr("href")]


def get_slice_count(ep_id: str, img_id: str) -> int:
  """计算图片切片数量"""
  aid_b64 = base64.b64encode(ep_id.encode()).decode()
  container_b64 = base64.b64encode(img_id.encode()).decode()

  combined = base64.b64decode(aid_b64).decode() + base64.b64decode(container_b64).decode()
  md5_hash = hashlib.md5(combined.encode()).hexdigest()
  last_char = md5_hash[-1]
  char_code = ord(last_char)

  aid_number = int(ep_id)
  if 268850 <= aid_number <= 421925:
    mod = char_code % 10
  elif aid_number >= 421926:
    mod = char_code % 8
  else:
    mod = char_code % 10

  slice_mapping = {0: 2, 1: 4, 2: 6, 3: 8, 4: 10, 5: 12, 6: 14, 7: 16, 8: 18, 9: 20}
  return slice_mapping.get(mod, 10)


def restore_scrambled_image(image_data: bytes, ep_id: str, img_id: str) -> Optional[Image.Image]:
  """还原混淆图片"""
  try:
    with Image.open(BytesIO(image_data)) as img:
      width, height = img.size
      slice_count = get_slice_count(ep_id, img_id)

      remainder = int(height % slice_count)
      base_height = height // slice_count
      slice_heights = list(reversed([base_height + remainder] + [base_height] * (slice_count - 1)))

      if sum(slice_heights) != height:
        raise ValueError("切片高度计算错误")

      y_pos = 0
      slices = []
      for h in slice_heights:
        slice_img = img.crop((0, y_pos, width, y_pos + h))
        slices.append(slice_img)
        y_pos += h

      restored = Image.new("RGB", (width, height))
      y_pos = 0
      for slice_img in reversed(slices):
        restored.paste(slice_img, (0, y_pos))
        y_pos += slice_img.height

      return restored
  except Exception as e:
    logger.error(f"图片还原失败: {e}")
    return None


def get_img_urls(session: requests.Session, chapter_url: str) -> list[str]:
  """获取章节图片URL"""
  try:
    response = fetch_with_retry(session, BASE_URL + chapter_url)
  except requests.RequestException as e:
    logger.error(f"请求图片列表失败: {e}")
    return []
  except RetryError as e:
    logger.error(f"重试失败: {e.last_attempt.exception()}")
    return []

  soup = BeautifulSoup(response.text, "lxml")
  img_tags = soup.select(".scramble-page > img[data-original]")
  return [str(img.get("data-original")) for img in img_tags]


@retry(stop=stop_after_attempt(RETRY_TIMES), wait=wait_fixed(WAIT_TIME))
def download_image(session: requests.Session, img_url: str, save_path: str) -> bool:
  """下载并保存单张图片"""
  try:
    parts = img_url.split("/")
    if len(parts) < 2:
      raise ValueError("无效的图片URL格式")

    ep_id, img_filename = parts[-2:]
    img_id = os.path.splitext(img_filename)[0]

    response = fetch_with_retry(session, img_url)

    # 还原图片
    restored_img = restore_scrambled_image(response.content, ep_id, img_id)
    if not restored_img:
      return False

    # 保存图片
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
      restored_img.save(f, format="WEBP" if img_url.endswith(".webp") else "JPEG")

    return True
  except Exception as e:
    logger.error(f"下载失败 {img_url}: {e}")
    return False


def convert_images_to_pdf(image_folder: str | Path, output_pdf: str | Path) -> None:
  """将图片转换为PDF"""
  valid_extensions = (".png", ".jpg", ".jpeg", ".webp")
  sorted_images = natsorted([os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(valid_extensions)])

  if not sorted_images:
    raise ValueError(f"目录中没有图片文件: {image_folder}")

  images = []
  for img_path in sorted_images:
    try:
      img = Image.open(img_path)
      if img.mode == "RGBA":
        img = img.convert("RGB")
      images.append(img)
    except Exception as e:
      logger.error(f"无法打开图片 {img_path}: {e}")

  if not images:
    raise ValueError("没有有效的图片可生成PDF")

  images[0].save(output_pdf, "PDF", resolution=100.0, save_all=True, append_images=images[1:])
  logger.info(f"PDF已生成: {output_pdf}")
