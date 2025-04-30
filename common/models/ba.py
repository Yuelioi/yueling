from typing import ClassVar

from tortoise import fields, models

# 定义模型


class Image(models.Model):
  id = fields.BigIntField(pk=True)  # 自增主键
  img_id = fields.TextField()
  hash = fields.TextField()

  title = fields.TextField()
  description = fields.TextField(null=True)
  tags = fields.JSONField()
  url = fields.TextField()
  meta = fields.JSONField(null=True)
  urls = fields.JSONField(null=True)
  page_count = fields.IntField(default=1)

  user_id = fields.TextField()
  user_name = fields.TextField()
  user_avatar = fields.TextField(null=True)

  width = fields.IntField()
  height = fields.IntField()
  bookmarks = fields.IntField()
  views = fields.IntField(null=True)

  source = fields.TextField()
  x_restrict = fields.IntField()
  ai_type = fields.IntField()

  created = fields.DatetimeField()
  updated = fields.DatetimeField(auto_now=True)

  size_kb = fields.IntField(default=0)
  file_ext = fields.TextField(default="")

  score = fields.IntField(default=0)

  class Meta:
    table = "image"
    indexes: ClassVar[list] = [
      ("bookmarks",),
      ("created",),
      ("user_id",),
      ("score",),
      ("x_restrict",),
      ("ai_type",),
      ("user_id", "id"),
    ]
    unique_together = ("img_id", "page_count")
