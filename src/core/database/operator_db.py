# -*- coding: utf-8 -*-

from loguru import logger
from peewee import *  # https://docs.peewee-orm.com/en/latest/index.html

from src.core.config.config import DB_NAME
from src.core.database.database import Person

# Настраиваем синхронную базу данных SQLite
db = SqliteDatabase(f"src/core/database/{DB_NAME}")


def get_operator_db(id_user):
    """Получаем данные оператора из БД (логин и пароль)"""
    with db:
        data = Person.get_or_none(
            Person.id_user == id_user
        )
        return data.username, data.password


def get_operator_table(user_id):
    """Получение таблицы операторов из БД"""
    # Настраиваем синхронную базу данных SQLite
    db = SqliteDatabase(f"src/core/database/{user_id}.db")
    db.connect()
    # Получаем список таблиц
    tables = db.get_tables()
    logger.info(tables)
    return tables
