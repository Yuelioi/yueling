"""OCR 文字识别 — RapidOCR 本地引擎"""

import asyncio

from rapidocr_onnxruntime import RapidOCR

from services.http_fetch import fetch_image

_engine = RapidOCR()


async def do_ocr(image_url: str, language: str = "chi_sim") -> str:
  """下载图片并执行本地 OCR"""
  img_buf = await fetch_image(image_url)
  img_bytes = img_buf.getvalue()

  result, _ = await asyncio.to_thread(_engine, img_bytes)
  if not result:
    return "未识别出文字"

  lines = [line[1] for line in result]
  return "\n".join(lines).strip() or "未识别出文字"
