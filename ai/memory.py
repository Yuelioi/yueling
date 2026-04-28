"""三层记忆系统 — Semantic(事实偏好) + Episodic(交互模式) + Procedural(群规则)"""

import time
from dataclasses import dataclass, field

from nonebot import logger
from sqlalchemy import Column, Float, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base, async_session

MAX_SEMANTIC_PER_USER = 100
MAX_EPISODIC_PER_USER = 50
MAX_PROCEDURAL_PER_GROUP = 10
DECAY_RATE = 0.95


# ─── ORM Models ──────────────────────────────────────────────

class SemanticMemory(Base):
  __tablename__ = "memory_semantic"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
  content: Mapped[str] = mapped_column(Text, nullable=False)
  category: Mapped[str] = mapped_column(String(32), nullable=False, default="general")
  score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
  created_at: Mapped[float] = mapped_column(Float, nullable=False)
  last_accessed: Mapped[float] = mapped_column(Float, nullable=False)


class EpisodicMemory(Base):
  __tablename__ = "memory_episodic"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
  group_id: Mapped[int] = mapped_column(Integer, nullable=False)
  input_text: Mapped[str] = mapped_column(Text, nullable=False)
  tool_name: Mapped[str] = mapped_column(String(64), nullable=False)
  tool_args: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
  result_summary: Mapped[str] = mapped_column(Text, nullable=False)
  steps: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
  created_at: Mapped[float] = mapped_column(Float, nullable=False)


class ProceduralMemory(Base):
  __tablename__ = "memory_procedural"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  group_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
  rule: Mapped[str] = mapped_column(Text, nullable=False)
  priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
  created_by: Mapped[int] = mapped_column(Integer, nullable=False)
  created_at: Mapped[float] = mapped_column(Float, nullable=False)


# ─── Write Triggers ──────────────────────────────────────────

PREFERENCE_TRIGGERS = [
  "我喜欢", "我不喜欢", "我讨厌", "以后别", "以后不要",
  "我是", "我的", "叫我", "记住",
  "每次都", "总是", "从来不", "一直",
]


def should_write_semantic(text: str) -> bool:
  return any(trigger in text for trigger in PREFERENCE_TRIGGERS)


def should_store_episode(tool_name: str | None, steps: int, success: bool) -> bool:
  return success and tool_name is not None and steps <= 3


# ─── Memory Manager ──────────────────────────────────────────

class MemoryManager:
  async def write_semantic(self, user_id: int, content: str, category: str = "general"):
    now = time.time()
    async with async_session() as session:
      from sqlalchemy import select, func, delete

      count_stmt = select(func.count()).where(SemanticMemory.user_id == user_id)
      result = await session.execute(count_stmt)
      count = result.scalar() or 0

      if count >= MAX_SEMANTIC_PER_USER:
        lowest = await session.execute(
          select(SemanticMemory)
          .where(SemanticMemory.user_id == user_id)
          .order_by(SemanticMemory.score.asc())
          .limit(1)
        )
        row = lowest.scalar_one_or_none()
        if row:
          await session.delete(row)

      mem = SemanticMemory(
        user_id=user_id,
        content=content,
        category=category,
        score=1.0,
        created_at=now,
        last_accessed=now,
      )
      session.add(mem)
      await session.commit()

  async def write_episodic(
    self,
    user_id: int,
    group_id: int,
    input_text: str,
    tool_name: str,
    tool_args: str,
    result_summary: str,
    steps: int,
  ):
    now = time.time()
    async with async_session() as session:
      from sqlalchemy import select, func

      count_stmt = select(func.count()).where(EpisodicMemory.user_id == user_id)
      result = await session.execute(count_stmt)
      count = result.scalar() or 0

      if count >= MAX_EPISODIC_PER_USER:
        oldest = await session.execute(
          select(EpisodicMemory)
          .where(EpisodicMemory.user_id == user_id)
          .order_by(EpisodicMemory.created_at.asc())
          .limit(1)
        )
        row = oldest.scalar_one_or_none()
        if row:
          await session.delete(row)

      ep = EpisodicMemory(
        user_id=user_id,
        group_id=group_id,
        input_text=input_text,
        tool_name=tool_name,
        tool_args=tool_args,
        result_summary=result_summary,
        steps=steps,
        created_at=now,
      )
      session.add(ep)
      await session.commit()

  async def recall_semantic(self, user_id: int, limit: int = 10) -> list[dict]:
    now = time.time()
    async with async_session() as session:
      from sqlalchemy import select

      stmt = (
        select(SemanticMemory)
        .where(SemanticMemory.user_id == user_id)
        .order_by(SemanticMemory.score.desc())
        .limit(limit)
      )
      result = await session.execute(stmt)
      memories = []
      for row in result.scalars():
        days_old = (now - row.created_at) / 86400
        effective_score = row.score * (DECAY_RATE ** days_old)
        memories.append({
          "content": row.content,
          "category": row.category,
          "score": round(effective_score, 3),
        })
      return memories

  async def recall_episodic(self, user_id: int, limit: int = 5) -> list[dict]:
    async with async_session() as session:
      from sqlalchemy import select

      stmt = (
        select(EpisodicMemory)
        .where(EpisodicMemory.user_id == user_id)
        .order_by(EpisodicMemory.created_at.desc())
        .limit(limit)
      )
      result = await session.execute(stmt)
      return [
        {
          "input": row.input_text,
          "tool": row.tool_name,
          "result": row.result_summary,
        }
        for row in result.scalars()
      ]

  async def get_user_context(self, user_id: int) -> str:
    semantic = await self.recall_semantic(user_id, limit=5)
    if not semantic:
      return ""
    lines = ["用户偏好:"]
    for mem in semantic:
      lines.append(f"- {mem['content']}")
    return "\n".join(lines)

  async def get_group_rules(self, group_id: int) -> list[str]:
    async with async_session() as session:
      from sqlalchemy import select

      stmt = (
        select(ProceduralMemory)
        .where(ProceduralMemory.group_id == group_id)
        .order_by(ProceduralMemory.priority.desc(), ProceduralMemory.created_at.asc())
      )
      result = await session.execute(stmt)
      return [row.rule for row in result.scalars()]

  async def add_group_rule(self, group_id: int, rule: str, created_by: int) -> int:
    now = time.time()
    async with async_session() as session:
      from sqlalchemy import select, func

      count_stmt = select(func.count()).where(ProceduralMemory.group_id == group_id)
      result = await session.execute(count_stmt)
      count = result.scalar() or 0

      if count >= MAX_PROCEDURAL_PER_GROUP:
        raise ValueError(f"群规则已达上限 ({MAX_PROCEDURAL_PER_GROUP} 条)")

      mem = ProceduralMemory(
        group_id=group_id,
        rule=rule,
        priority=0,
        created_by=created_by,
        created_at=now,
      )
      session.add(mem)
      await session.commit()
      await session.refresh(mem)
      return mem.id

  async def remove_group_rule(self, group_id: int, rule_id: int) -> bool:
    async with async_session() as session:
      from sqlalchemy import select

      stmt = select(ProceduralMemory).where(
        ProceduralMemory.id == rule_id,
        ProceduralMemory.group_id == group_id,
      )
      result = await session.execute(stmt)
      row = result.scalar_one_or_none()
      if not row:
        return False
      await session.delete(row)
      await session.commit()
      return True

  async def list_group_rules(self, group_id: int) -> list[dict]:
    async with async_session() as session:
      from sqlalchemy import select

      stmt = (
        select(ProceduralMemory)
        .where(ProceduralMemory.group_id == group_id)
        .order_by(ProceduralMemory.priority.desc(), ProceduralMemory.created_at.asc())
      )
      result = await session.execute(stmt)
      return [
        {"id": row.id, "rule": row.rule, "created_by": row.created_by}
        for row in result.scalars()
      ]


memory_manager = MemoryManager()
