import os
import time
from pathlib import Path

import img2pdf  # 不支持webp
from natsort import natsorted
from PIL import Image


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
      return

  if not images:
    raise ValueError("没有有效的图片可生成PDF")

  images[0].save(output_pdf, "PDF", resolution=100.0, save_all=True, append_images=images[1:])


if __name__ == "__main__":
  root = Path("/projects/yueling/data/images/jm")

  # for img in imgs:
  #   print(img)
  start = time.time()
  images = sorted(root.rglob("*.webp"))
  with open("output.pdf", "wb") as f:
    f.write(img2pdf.convert([str(p) for p in images], rotation=img2pdf.Rotation.ifvalid))
  print(time.time() - start)
