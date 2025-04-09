import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Union

from common.config import config

MAX_WORKERS = 6

HASH_BLOCK_SIZE = 4096
database = config.resource.database
storage = config.resource.images
categories = ["吃的", "喝的", "拍一拍", "杂鱼", "水果", "沙雕图", "玩的", "福瑞", "美少女", "老公", "老婆", "表情", "语录", "零食", "龙图", "ba"]

recycle = config.resource.recycle


class ValidationResult:
  """校验结果容器"""

  def __init__(self):
    self.new_files: list[tuple[Path, str]] = []  # (文件路径, 计算出的哈希)
    self.changed_files: list[tuple[Path, str]] = []  # (文件路径, 哈希, 新文件名)
    self.unchanged_files: list[tuple[Path, str]] = []  # (文件路径, 哈希, 新文件名)
    self.need_clean: set[str] = set()  # 需要清理的哈希集合
    self.errors = []  # 错误信息


def calculate_hash(image_data: bytes | Path) -> str:
  """
  计算文件哈希
  :param image_data: 图片数据（可以是字节流或文件路径）
  """
  sha256 = hashlib.sha256()
  try:
    if isinstance(image_data, Path):
      with open(image_data, "rb") as f:
        for block in iter(lambda: f.read(HASH_BLOCK_SIZE), b""):
          sha256.update(block)
        return sha256.hexdigest()
    else:
      # 直接处理字节流，无需分块
      sha256.update(image_data)
      return sha256.hexdigest()
  except OSError as e:
    raise RuntimeError(f"文件读取失败: {e}")


@dataclass
class ImageData:
  """图片元数据类"""

  filename: str  # 文件名
  file_hash: str  # 哈希值
  category: str = ""  # 分类名称

  tags: list[str] = field(default_factory=list)  # 标签列表
  uploader: str = "anonymous"  # 上传者名称
  created_at: str = field(default_factory=lambda: datetime.now().isoformat())  # 创建时间

  def __hash__(self):
    return hash(self.file_hash)

  def __eq__(self, other):
    if isinstance(other, ImageData):
      return self.file_hash == other.file_hash
    return False

  def to_dict(self):
    """转换为字典格式"""
    return asdict(self)

  @classmethod
  def from_dict(cls, data: dict):
    """从字典创建实例"""
    return cls(**data)


@dataclass
class ImageStorage:
  """图片存储类 记录图片元数据"""

  category: str  # 分类名称
  db_path: Path  # 数据库路径
  keys: list[str] = field(default_factory=list)  # 数据库键列表
  data: dict[str, ImageData] = field(default_factory=dict)  # {hash: ImageData}

  def __post_init__(self):
    self.db_path.parent.mkdir(parents=True, exist_ok=True)
    self._load()

  def _load(self):
    """加载数据库"""

    if self.db_path.exists():
      with open(self.db_path, encoding="utf-8") as f:
        raw_data = json.load(f)
        self.data = {k: ImageData.from_dict(v) for k, v in raw_data.items()}

  def refresh(self):
    # 手动验证
    self._load()
    self._validate_storage()

  def _validate_storage(self):
    """异步校验文件与数据库一致性"""
    storage_dir = storage / self.category
    # 准备校验数据
    validation_result = ValidationResult()
    existing_hashes = set(self.data.keys())
    file_queue = list(storage_dir.glob("*.*"))

    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
      futures = []
      for img_file in file_queue:
        if img_file.suffix.lower() not in (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"):
          continue
        futures.append(executor.submit(self._process_single_file, img_file, existing_hashes))

      # 收集处理结果
      for future in as_completed(futures):
        try:
          result = future.result()
          if isinstance(result, Exception):
            validation_result.errors.append(str(result))
            continue

          filepath, file_hash, action = result
          if action == "new":
            validation_result.new_files.append((filepath, file_hash))
          elif action == "changed":
            validation_result.changed_files.append((filepath, file_hash))
          else:
            validation_result.unchanged_files.append((filepath, file_hash))
        except Exception as e:
          validation_result.errors.append(str(e))

    # 主线程处理结果
    self._apply_validation_result(validation_result, existing_hashes)

    for file_hash in validation_result.need_clean:
      self.data.pop(file_hash, None)

    # 批量保存修改
    self.save()

    for s in validation_result.errors:
      print(f"校验失败: {s}")
    # 输出统计信息
    print(
      f"{self.category}校验完成: 新增 {len(validation_result.new_files)} | 变更 {len(validation_result.changed_files)} | 错误 {len(validation_result.errors)}"
    )

  def _process_single_file(self, img_file: Path, existing_hashes: set) -> Union[tuple[Path, str | None, str], Exception]:
    """单个文件处理任务（在子线程中执行）"""
    try:
      file_hash = calculate_hash(img_file)

      # 判断文件状态
      if file_hash not in existing_hashes:
        return (img_file, file_hash, "new")

      record = self.data[file_hash]
      if record.filename != img_file.name or record.category != self.category:
        return (img_file, file_hash, "changed")

      return (img_file, file_hash, "unchanged")
    except Exception as e:
      return e

  def _apply_validation_result(self, result: ValidationResult, existing_hashes: set):
    """应用校验结果"""
    # 处理新增文件
    for img_file, file_hash in result.new_files:
      self.data[file_hash] = ImageData(filename=img_file.name, category=self.category, file_hash=file_hash, uploader="system")

    # 处理文件名变更
    for new_name, file_hash in result.changed_files:
      filepath = storage / self.category / self.data[file_hash].filename
      if filepath.exists() and filepath.name != new_name.name:
        self.delete_image(file_hash, remove_file=True)
        continue
      self.data[file_hash].filename = new_name.name
      self.data[file_hash].category = self.category

    # 记录需要保留的哈希
    current_hashes = {fh for _, fh in result.new_files} | {fh for _, fh in result.changed_files} | {fh for _, fh in result.unchanged_files}
    need_clean = existing_hashes - current_hashes
    result.need_clean.update(need_clean)

  def add_image(
    self, image_data: bytes, suffix: str, filename: str = "", uploader: str = "anonymous", tags: list[str] = [], auto_save: bool = True
  ) -> ImageData:
    """添加新图片"""

    # 文件重复性检查
    file_hash = calculate_hash(image_data)
    if file_hash in self.data:
      raise ValueError("相同哈希的图片已存在")

    # 存储文件
    if not filename:
      filename = file_hash
    target_path = storage / self.category / f"{filename}.{suffix}"

    with open(target_path, "wb") as f:
      f.write(image_data)

    # 创建记录
    imd = ImageData(filename=filename, category=self.category, file_hash=file_hash, uploader=uploader, tags=tags)
    self.data[file_hash] = imd
    if auto_save:
      self.save()
    return imd

  def delete_image(self, file_hash: str, remove_file: bool = True, auto_save: bool = True):
    """删除图片记录和文件"""
    if file_hash not in self.data:
      return

    # 删除文件
    if remove_file:
      img_path = storage / self.category / self.data[file_hash].filename
      if img_path.exists():
        try:
          target_path = recycle / img_path.name
          img_path.replace(target_path)
        except Exception as e:
          print(f"文件删除失败: {img_path} - {str(e)}")

    # 删除记录
    del self.data[file_hash]
    if auto_save:
      self.save()

  def add_tags(self, file_hash: str, tags: list[str]):
    """添加标签"""
    if file_hash not in self.data:
      raise KeyError("图片不存在")

    img = self.data[file_hash]
    new_tags = [t for t in tags if t not in img.tags]
    img.tags.extend(new_tags)
    self.save()
    return new_tags

  def save(self):
    """原子化保存数据库"""
    try:
      temp_path = self.db_path.with_suffix(".tmp")
      with open(temp_path, "w", encoding="utf-8") as f:
        json.dump({k: v.to_dict() for k, v in self.data.items()}, f, indent=2, ensure_ascii=False)
      temp_path.replace(self.db_path)
    except Exception as e:
      if temp_path.exists():
        temp_path.unlink()
      raise RuntimeError(f"数据库保存失败: {e}")


class ImageDatabase:
  """图片数据库类"""

  def __init__(
    self,
  ):
    self.storages: dict[str, ImageStorage] = {}
    self.tag_index: dict[str, set[ImageData]] = {}
    self._initialize()

  def _initialize(self):
    """初始化数据库"""
    for category in categories:
      storage = ImageStorage(category=category, db_path=database / f"{category}_db.json")
      self.storages[category] = storage
    self._rebuild_index()

  def _rebuild_index(self):
    """重建标签索引"""
    self.tag_index.clear()
    for storage in self.storages.values():
      for img_data in storage.data.values():
        for tag in img_data.tags:
          self._add_to_index(tag, img_data)

  def _add_to_index(self, tag: str, imagedata: ImageData):
    """维护标签反向索引"""
    if tag not in self.tag_index:
      self.tag_index[tag] = set()
    self.tag_index[tag].add(imagedata)

  def _remove_from_index(self, tag: str, imagedata: ImageData):
    """从索引移除记录"""
    if tag in self.tag_index:
      self.tag_index[tag].discard(imagedata)
      if not self.tag_index[tag]:
        del self.tag_index[tag]

  def add_image(self, category: str, image_data: bytes, suffix: str, filename: str = "", tags: list[str] = [], uploader: str = "anonymous") -> ImageData:
    """添加图片到指定分类"""
    if category not in self.storages:
      raise ValueError(f"无效分类: {category}")

    storage = self.storages[category]
    im = storage.add_image(image_data=image_data, suffix=suffix, filename=filename, uploader=uploader, tags=tags or [])

    # 更新索引
    if tags:
      for tag in tags:
        self._add_to_index(tag, im)
    return im

  def delete_image(self, file_hash: str):
    """删除指定图片"""
    found = False
    for storage in self.storages.values():
      if file_hash in storage.data:
        img_data = storage.data[file_hash]
        # 移除所有相关标签
        for tag in img_data.tags:
          self._remove_from_index(tag, img_data)
        storage.delete_image(file_hash)
        found = True
        break
    if not found:
      raise KeyError("图片不存在")

  def update_tags(self, file_hash: str, new_tags: list[str]):
    """更新图片标签"""
    # 查找图片
    img = None
    for storage in self.storages.values():
      if file_hash in storage.data:
        img = storage.data[file_hash]
        break
    if not img:
      raise KeyError("图片不存在")

    # 计算变化
    old_tags = set(img.tags)
    new_tags_set = set(new_tags)
    added = new_tags_set - old_tags
    removed = old_tags - new_tags_set

    # 更新存储
    img.tags = list(new_tags_set)  # 直接替换标签列表
    storage = self.storages[img.category]
    storage.save()

    # 更新索引
    for tag in removed:
      self._remove_from_index(tag, img)
    for tag in added:
      self._add_to_index(tag, img)

  def search_images_by_tag(self, cat: str, tags: list[str]) -> list[ImageData]:
    """按标签检索"""
    if not tags:
      return []

    # 获取所有标签对应的集合
    sets = [self.tag_index.get(tag, set()) for tag in tags]
    if not sets:
      return []

    # 计算交集并过滤分类
    try:
      common = set.intersection(*sets)
    except TypeError:
      return []
    return [img for img in common if img.category == cat]

  def search_image_by_hash(self, file_data: bytes) -> list[str] | None:
    """获取图片详情"""

    file_hash = calculate_hash(file_data)
    for storage in self.storages.values():
      if file_hash in storage.data:
        return storage.data[file_hash].tags
    return None

  def tags(self, cat: str, n: int):
    # 统计每个标签下满足条件的元素数量

    if cat:
      tag_counts = {tag: sum(1 for v in values if v.category == cat) for tag, values in self.tag_index.items()}
    else:
      tag_counts = {tag: len(values) for tag, values in self.tag_index.items()}

    # 按数量降序排序并取前x个标签

    top_tags = [
      [tag, count]
      for tag, count in sorted(
        tag_counts.items(),
        key=lambda item: item[1],
        reverse=True,
      )[:n]  # 取前n个
    ]

    return top_tags


def batch_add_images(db: ImageDatabase, image_folder: Path, tag_folder: Path):
  # 预处理收集所有文件信息
  file_infos = []
  for file in image_folder.glob("*.*"):
    tag_file = tag_folder / f"{file.stem}.txt"
    try:
      with open(tag_file, "r", encoding="utf-8") as f:
        tags = [t.strip() for t in f.read().split(",") if t.strip()]
      file_infos.append((file, "user123", tags))
    except FileNotFoundError:
      print(f"跳过 {file.name}: 标签文件不存在")


idb = ImageDatabase()
