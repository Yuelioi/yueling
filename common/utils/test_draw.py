from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image, ImageFont

from .draw import draw_grid  # Replace 'your_module' with the actual module name


@pytest.fixture
def image_files():
  # Create mock image files for testing
  images = []
  for i in range(4):
    img = Image.new("RGB", (100, 100), color=0)
    img_path = Path(f"test_image_{i}.png")
    img.save(img_path)
    images.append(img_path)
  yield images
  # Clean up the mock image files after testing
  for img_path in images:
    img_path.unlink()


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


def test_draw_grid_five_files(image_files):
  result = draw_grid(image_files[:5], rows=3, cols=2)
  assert isinstance(result, BytesIO)
  result.seek(0)
  img = Image.open(result)
  assert img.size == (750, 1125)


def test_draw_grid_custom_grid_width(image_files):
  result = draw_grid(image_files[:4], grid_width=500)
  assert isinstance(result, BytesIO)
  result.seek(0)
  img = Image.open(result)
  assert img.size == (500, 500)


def test_draw_grid_with_font(image_files, tmp_path):
  font_path = tmp_path / "test_font.ttf"
  ImageFont.FreeTypeFont(str(font_path), 36)  # Create a mock font file
  result = draw_grid(image_files[:4], font_path=font_path)
  assert isinstance(result, BytesIO)
  result.seek(0)
  img = Image.open(result)
  assert img.size == (750, 750)


def test_draw_grid_with_non_image_file(tmp_path):
  non_image_path = tmp_path / "test_file.txt"
  non_image_path.write_text("This is not an image file")
  with pytest.raises((OSError, IOError)):
    draw_grid([non_image_path])
