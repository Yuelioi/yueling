from dataclasses import dataclass, field
from datetime import datetime

from common.models.base import Element


@dataclass
class ImageData(Element):
  path: str = ""
  category: str = ""
  uploader: int = 0
  upload_time: datetime = field(default_factory=datetime.now)
  hash: str = ""
  score: int = 0
