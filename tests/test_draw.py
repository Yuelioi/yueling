from io import BytesIO

import pytest
from PIL import Image

from services.draw import draw_grid


@pytest.fixture
def image_files(tmp_path):
  images = []
  for i in range(4):
    img = Image.new("RGB", (100, 100), color=0)
    img_path = tmp_path / f"test_image_{i}.png"
    img.save(img_path)
    images.append(img_path)
  return images


def test_draw_grid_happy_path(image_files):
  result = draw_grid(image_files)
  assert isinstance(result, BytesIO)
  result.seek(0)
  img = Image.open(result)
  assert img.size == (750, 750)


def test_draw_grid_no_files():
  result = draw_grid([])
  assert isinstance(result, BytesIO)
  result.seek(0)
  img = Image.open(result)
  assert img.size == (750, 750)


def test_draw_grid_one_file(image_files):
  result = draw_grid(image_files[:1])
  assert isinstance(result, BytesIO)
  result.seek(0)
  img = Image.open(result)
  assert img.size == (750, 750)


def test_draw_grid_four_files(image_files):
  result = draw_grid(image_files[:4], rows=2, cols=2)
  assert isinstance(result, BytesIO)
  result.seek(0)
  img = Image.open(result)
  assert img.size == (750, 750)


def test_draw_grid_with_non_image_file(tmp_path):
  non_image_path = tmp_path / "test_file.txt"
  non_image_path.write_text("This is not an image file")
  with pytest.raises((OSError, IOError)):
    draw_grid([non_image_path])
