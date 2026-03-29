"""Работа с базой данных SQLite."""

import aiosqlite
import logging

logger = logging.getLogger(__name__)

DB_PATH = "data/bot.db"


async def init_db():
    """Создать таблицу если не существует."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER NOT NULL,
                role      TEXT NOT NULL,
                content   TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()
        logger.info("БД инициализирована")


async def save_message(user_id: int, role: str, content: str):
    """Сохранить сообщение в БД."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content)
        )
        await db.commit()


async def get_history(user_id: int) -> list:
    """Получить историю диалога пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT role, content FROM messages WHERE user_id = ? ORDER BY timestamp",
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [{"role": row[0], "content": row[1]} for row in rows]