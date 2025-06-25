# -*- coding: utf-8 -*-
from typing import Optional
from typing import Union

import aiosqlite
from loguru import logger

from config import DB_NAME


class DataBase:
    def __init__(self, filename: str):
        self._filename = filename

    async def open(self) -> aiosqlite.Connection:
        return await aiosqlite.connect(self._filename)

    async def create_tables(self) -> None:
        """
        Асинхронно создаёт таблицы в базе данных при их отсутствии.
        Также настраивает параметры SQLite для повышения производительности.
        """
        try:
            # Открываем соединение с базой данных
            conn = await self.open()
            # Включаем режим WAL (Write-Ahead Logging), чтобы улучшить параллелизм и скорость записи
            await conn.execute("PRAGMA journal_mode=WAL")
            # Устанавливаем уровень синхронизации диска в NORMAL — хороший баланс между скоростью и надёжностью
            await conn.execute("PRAGMA synchronous=NORMAL")
            # Выполняем внутренние оптимизации БД, чтобы повысить производительность
            await conn.execute("PRAGMA optimize")
            # Создаём таблицу пользователей, если она ещё не существует
            # Хранит ID пользователя и его язык (для мультиязычности)
            await conn.execute("""CREATE TABLE IF NOT EXISTS users
                                  (
                                      user_id INTEGER PRIMARY KEY,
                                      lang    TEXT
                                  )""")
            # Таблица статусов обращений. Используется как справочник (статусы: "открыт", "в обработке", "закрыт" и т.д.)
            await conn.execute(
                """CREATE TABLE IF NOT EXISTS statuses
                   (
                       id     INTEGER PRIMARY KEY AUTOINCREMENT,
                       status TEXT UNIQUE
                   )""")
            # Основная таблица обращений (тикетов)
            # Ссылается на пользователей и статусы через внешние ключи
            await conn.execute("""
                               CREATE TABLE IF NOT EXISTS appeals
                               (
                                   id              INTEGER PRIMARY KEY AUTOINCREMENT,
                                   user_id         INTEGER,           -- кто создал обращение
                                   manager_id      INTEGER,           -- кто из менеджеров его обрабатывает
                                   status_id       INTEGER DEFAULT 1, -- текущий статус (по умолчанию — первый статус)
                                   rating          INTEGER,           -- оценка после закрытия обращения
                                   last_message_at TEXT,              -- время последнего сообщения
                                   FOREIGN KEY (user_id) REFERENCES users (user_id),
                                   FOREIGN KEY (manager_id) REFERENCES users (user_id),
                                   FOREIGN KEY (status_id) REFERENCES statuses (id)
                               )
                               """)
            # Добавляем стандартные статусы в таблицу statuses (например: 'open', 'closed')
            await self.add_statuses()
            # Сохраняем изменения в базе данных
            await conn.commit()
            logger.info("Таблицы успешно созданы или уже существуют")
        except Exception as e:
            # Логируем ошибку, если что-то пошло не так
            logger.error(f"Ошибка при создании таблиц: {e}")

    async def add_statuses(self):
        try:
            conn = await self.open()
            statuses = ["В ожидании", "В обработке", "Закрыто"]
            for status in statuses:
                await conn.execute("""INSERT OR IGNORE INTO statuses (status)
                                      VALUES (?)""", (status,))
            await conn.commit()
            logger.info("Статусы добавлены")
        except Exception as e:
            logger.error(f"Ошибка добавления статусов: {e}")

    async def get_status_name(self, status_id: int) -> str:
        try:
            conn = await self.open()
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("SELECT status FROM statuses WHERE id = ?", (status_id,))
            status = await cursor.fetchone()
            return status[0] if status else ''
        except Exception as e:
            logger.error(f"Ошибка получения названия статуса: {e}")
            return {}

    async def add_user(self, user_id: int, lang: str):
        try:
            conn = await self.open()
            await conn.execute(
                """INSERT INTO users (user_id, lang)
                   VALUES (?, ?)
                   ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang""",
                (user_id, lang))
            await conn.commit()
        except Exception as e:
            logger.error(f"Ошибка добавления пользователя {user_id}: {e}")

    async def update_appeal_data(self, appeal_id: int, **kwargs):
        try:
            conn = await self.open()
            keys = ', '.join(f"{key} = ?" for key in kwargs.keys())
            values = list(kwargs.values())
            values.append(appeal_id)
            await conn.execute(f"UPDATE appeals SET {keys} WHERE id = ?", values)
            await conn.commit()
        except Exception as e:
            logger.error(f"Ошибка добавления менеджера к обращению {appeal_id}: {e}")

    async def get_user(self, user_id: int) -> dict:
        try:
            conn = await self.open()
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = await cursor.fetchone()
            return dict(row) if row else {}
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {user_id}: {e}")
            return {}

    async def get_user_lang(self, user_id: int) -> Optional[str]:
        try:
            conn = await self.open()
            cursor = await conn.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
            lang = await cursor.fetchone()
            return lang[0] if lang else None
        except Exception as e:
            logger.error(f"Ошибка получения языка {user_id}: {e}")

    async def add_appeal(self, user_id: int, status_id: int = 1) -> int:
        """Добавление обращения с указанием статуса"""
        try:
            conn = await self.open()
            cursor = await conn.execute("SELECT id FROM statuses")
            statuses = await cursor.fetchall()

            if (status_id,) not in statuses:
                logger.critical(f"Отсутствует status_id = {status_id}")
                status_id = 1

            cursor = await conn.execute("""INSERT INTO appeals (user_id, status_id)
                                           VALUES (?, ?)""",
                                        (user_id, status_id))
            appeal_id = cursor.lastrowid
            await conn.commit()
            return appeal_id if appeal_id else 0
        except Exception as e:
            logger.error(f"Ошибка добавления обращения {user_id}: {e}")
            return 0

    async def get_appeal(self, **kwargs) -> Union[dict, list[dict]]:
        try:
            conn = await self.open()
            conn.row_factory = aiosqlite.Row

            conditions = []
            values = []
            for key, value in kwargs.items():
                conditions.append(f"{key} = ?")
                values.append(value)

            sql = "SELECT * FROM appeals"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)

            cursor = await conn.execute(sql, values)
            rows = await cursor.fetchall()

            if not rows:
                return {}
            elif len(rows) == 1:
                return dict(rows[0])
            else:
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка получения обращения: {e}")
            return {}

    async def check_user_active_appeal(self, user_id) -> bool:
        try:
            conn = await self.open()
            cursor = await conn.execute(
                "SELECT EXISTS(SELECT 1 FROM appeals WHERE user_id = ? AND status_id IN (1, 2)) LIMIT 1", (user_id,))
            result = await cursor.fetchone()
            return bool(result[0]) if result else False
        except Exception as e:
            logger.error(f"Ошибка проверки на активные обращения пользователя: {e}")
            return {}

    async def check_manager_active_appeal(self, manager_id) -> bool:
        try:
            conn = await self.open()
            cursor = await conn.execute(
                "SELECT EXISTS(SELECT 1 FROM appeals WHERE manager_id = ? AND status_id IN (1, 2)) LIMIT 1",
                (manager_id,))
            result = await cursor.fetchone()
            return bool(result[0]) if result else False
        except Exception as e:
            logger.error(f"Ошибка проверки на активные обращения менеджера: {e}")
            return {}


db = DataBase(filename=f"database/{DB_NAME}")
