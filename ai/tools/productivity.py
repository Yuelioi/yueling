"""AI 内置工具 — 生产力（待办清单、点歌、以图搜图）"""

import time

from sqlalchemy import Integer, Float, Text, Boolean, select, func
from sqlalchemy.orm import Mapped, mapped_column

from ai.registry import tool
from core.context import ToolContext
from core.database import Base, async_session
from core.http import get_client
from services.http_fetch import fetch_image


# ─── 待办数据模型 ──────────────────────────────────────────

class TodoItem(Base):
  __tablename__ = "todo_items"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
  group_id: Mapped[int] = mapped_column(Integer, nullable=False)
  content: Mapped[str] = mapped_column(Text, nullable=False)
  done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
  created_at: Mapped[float] = mapped_column(Float, nullable=False)


async def _get_undone_todos(user_id: int):
  async with async_session() as session:
    items = (await session.execute(
      select(TodoItem)
      .where(TodoItem.user_id == user_id, TodoItem.done == False)
      .order_by(TodoItem.created_at.asc())
    )).scalars().all()
    return session, items


# ─── 待办清单 ──────────────────────────────────────────────

@tool(
  tags=["info"],
  examples=["帮我记一下明天交报告", "我的待办", "完成第1个待办", "删除待办"],
)
async def manage_todo(ctx: ToolContext, action: str, content: str = "", item_id: int = 0) -> str:
  """管理个人待办清单

  Args:
    action: 操作(add/list/done/remove)
    content: 待办内容(add时必填)
    item_id: 待办编号(done/remove时必填)
  """
  user_id = ctx.user_id

  if action == "add":
    if not content:
      return "请说明待办内容"
    async with async_session() as session:
      result = await session.execute(
        select(func.count()).where(TodoItem.user_id == user_id, TodoItem.done == False)
      )
      if (result.scalar() or 0) >= 20:
        return "待办太多了，先完成一些吧（上限20条）"
      session.add(TodoItem(
        user_id=user_id, group_id=ctx.group_id,
        content=content, created_at=time.time(),
      ))
      await session.commit()
    return f"已添加待办: {content}"

  elif action == "list":
    session, items = await _get_undone_todos(user_id)
    if not items:
      return "你没有待办事项"
    lines = [f"{i}. {item.content}" for i, item in enumerate(items, 1)]
    return "你的待办:\n" + "\n".join(lines)

  elif action in ("done", "remove"):
    if item_id <= 0:
      return "请指定待办编号"
    session, items = await _get_undone_todos(user_id)
    if item_id > len(items):
      return f"编号超出范围（共{len(items)}条）"
    target = items[item_id - 1]
    async with async_session() as s:
      obj = await s.get(TodoItem, target.id)
      if action == "done":
        obj.done = True
        await s.commit()
        return f"已完成: {target.content}"
      else:
        await s.delete(obj)
        await s.commit()
        return f"已删除: {target.content}"

  return "未知操作，支持: add/list/done/remove"


# ─── 点歌 ─────────────────────────────────────────────────

@tool(
  tags=["fun", "search"],
  examples=["帮我点一首周杰伦的歌", "搜一下晴天", "来首歌"],
)
async def search_music(ctx: ToolContext, keyword: str) -> str:
  """搜索音乐，返回歌曲信息

  Args:
    keyword: 歌曲名或歌手名
  """
  try:
    client = get_client()
    resp = await client.get(
      f"https://api.vvhan.com/api/music/wy?kw={keyword}&type=json",
      timeout=10,
    )
    if resp.status_code != 200:
      return "搜索失败"
    data = resp.json()
    if not data.get("success"):
      return f"没找到'{keyword}'相关的歌曲"
    info = data.get("info", {})
    name = info.get("name", keyword)
    author = info.get("auther", "未知")
    url = info.get("url", "")
    result = f"🎵 {name} - {author}"
    if url:
      result += f"\n🔗 {url}"
    return result
  except Exception as e:
    return f"搜索失败: {e}"


# ─── 以图搜图 ─────────────────────────────────────────────

@tool(
  tags=["image", "search"],
  examples=["帮我搜一下这张图的出处", "以图搜图", "这张图是哪来的"],
)
async def reverse_image_search(ctx: ToolContext) -> str:
  """用图片搜索原始来源（需要消息附带图片）"""
  imgs = ctx.get_images()
  if not imgs:
    return "请在消息中附带图片"

  try:
    img_buf = await fetch_image(imgs[0])
    client = get_client()
    resp = await client.post(
      "https://saucenao.com/search.php",
      files={"file": ("image.jpg", img_buf.getvalue(), "image/jpeg")},
      data={"output_type": 2, "numres": 3, "db": 999},
      timeout=20,
    )
    if resp.status_code != 200:
      return "搜索失败"
    data = resp.json()
    results = data.get("results", [])
    if not results:
      return "没有找到匹配的图片来源"

    lines = []
    for r in results[:3]:
      header = r.get("header", {})
      sim = header.get("similarity", "?")
      data_r = r.get("data", {})
      title = data_r.get("title", "") or data_r.get("source", "") or data_r.get("material", "")
      urls = data_r.get("ext_urls", [])
      author = data_r.get("author_name", "") or data_r.get("member_name", "") or data_r.get("creator", "")
      line = f"[{sim}%] {title}"
      if author:
        line += f" by {author}"
      if urls:
        line += f"\n  {urls[0]}"
      lines.append(line)

    return "搜图结果:\n" + "\n".join(lines)
  except Exception as e:
    return f"搜图失败: {e}"
