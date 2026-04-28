"""
数据迁移脚本：从旧 SQLite 数据库迁移到新统一数据库

用法: python -m scripts.migrate_data
"""
import asyncio
import sqlite3
from pathlib import Path


from core.database import Base, async_session, engine
from models import (
    AutoReply,
    ClockInRecord,
    GroupFileRecord,
    PkBuff,
    PkStatus,
    PkUser,
)


OLD_DATA_DB = Path("data/database/data.db")
OLD_PK_DB = Path("data/pk/pk.db")


def read_old_table(db_path: Path, table_name: str) -> list[dict]:
    if not db_path.exists():
        print(f"  跳过: {db_path} 不存在")
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = [dict(row) for row in cursor.fetchall()]
        print(f"  读取 {table_name}: {len(rows)} 条记录")
        return rows
    except sqlite3.OperationalError as e:
        print(f"  跳过 {table_name}: {e}")
        return []
    finally:
        conn.close()


async def migrate():
    print("=== 开始数据迁移 ===\n")

    # 创建新表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("新数据库表已创建\n")

    # 迁移 data.db 中的表
    print("--- 迁移 data.db ---")
    groupfiles = read_old_table(OLD_DATA_DB, "groupfiles")
    records = read_old_table(OLD_DATA_DB, "record")
    replies = read_old_table(OLD_DATA_DB, "reply")

    # 迁移 pk.db 中的表
    print("\n--- 迁移 pk.db ---")
    users = read_old_table(OLD_PK_DB, "users")
    statuses = read_old_table(OLD_PK_DB, "status")
    buffs = read_old_table(OLD_PK_DB, "buffs")

    async with async_session() as session:
        # 群文件记录
        for row in groupfiles:
            session.add(GroupFileRecord(
                group_id=row.get("group_id", 0),
                file_id=row["file_id"],
                file_name=row["file_name"],
                busid=row["busid"],
                file_size=row.get("file_size"),
                upload_time=row.get("upload_time"),
                dead_time=row.get("dead_time"),
                modify_time=row.get("modify_time"),
                download_times=row.get("download_times"),
                uploader=row.get("uploader"),
                uploader_name=row.get("uploader_name"),
            ))

        # 打卡记录
        for row in records:
            session.add(ClockInRecord(
                qq=row["qq"],
                target=row.get("target"),
                last_record_time=row.get("last_record_time"),
            ))

        # 自动回复
        for row in replies:
            session.add(AutoReply(
                qq=row["qq"],
                keyword=row.get("keyword"),
                reply=row.get("reply"),
                group=row.get("group"),
            ))

        # PK 用户
        for row in users:
            session.add(PkUser(
                user_id=row["user_id"],
                nickname=row["nickname"],
                power=row.get("power", 0),
                money=row.get("money", 0),
            ))

        # PK 状态
        for row in statuses:
            session.add(PkStatus(
                user_id=row["user_id"],
                name=row["name"],
                description=row.get("description", ""),
                duration=str(row["duration"]) if row.get("duration") else None,
            ))

        # PK 增益
        for row in buffs:
            session.add(PkBuff(
                user_id=row["user_id"],
                name=row["name"],
                description=row.get("description", ""),
                duration=str(row["duration"]) if row.get("duration") else None,
            ))

        await session.commit()

    print("\n=== 迁移完成 ===")
    print(f"群文件: {len(groupfiles)} 条")
    print(f"打卡: {len(records)} 条")
    print(f"回复: {len(replies)} 条")
    print(f"PK用户: {len(users)} 条")
    print(f"PK状态: {len(statuses)} 条")
    print(f"PK增益: {len(buffs)} 条")


if __name__ == "__main__":
    asyncio.run(migrate())
