# -*- coding: utf-8 -*-
from datetime import datetime

from peewee import *  # https://docs.peewee-orm.com/en/latest/index.html


def create_tables(name_db, appeal_id):
    """Создание таблиц в базе данных

    :param name_db: ID оператора
    :param appeal_id: ID обращения
    """

    # Настраиваем синхронную базу данных SQLite
    db = SqliteDatabase(f"src/core/database/{name_db}.db")
    appeal_id = f"{appeal_id}"

    class Dialogues(Model):
        user_id = CharField(null=True)  # Кто создал обращение (ID Telegram пользователя)
        operator_id = CharField(null=True)  # Кто обрабатывает (ID Telegram оператора)
        message_text = CharField(null=True)  # Текст сообщения
        last_message_at = DateTimeField(default=datetime.now)  # Время последнего сообщения

        class Meta:
            database = db
            table_name = f"{appeal_id}"  # Имя таблицы

    db.connect()  # Создаем базу данных
    db.create_tables([Dialogues], safe=True)  # Создаем таблицу
    return Dialogues  # Возвращаем класс


def write_to_db(appeal_id, operator_id, user_id, message_text, name_db):
    """Запись в базу данных

    :param appeal_id: ID обращения
    :param user_id: ID пользователя
    :param operator_id: ID оператора
    :param message_text: Текст сообщения
    :param name_db: Имя базы данных
    """

    dialog_model = create_tables(name_db=name_db, appeal_id=appeal_id, )
    # Пример добавления записи
    dialog_model.create(
        user_id=user_id,  # ID пользователя
        operator_id=operator_id,  # ID оператора
        message_text=message_text,  # Текст сообщения
        last_message_at=datetime.now()  # Время последнего сообщения
    )


def get_operator_dialog(name_db: str, appeal_id: str):
    """Получаем все сообщения из определённой таблицы обращения для оператора

    :param name_db: ID оператора (имя базы данных)
    :param appeal_id: ID обращения (имя таблицы)
    :return: список словарей с сообщениями
    """
    db = SqliteDatabase(f"src/core/database/{name_db}.db")
    dialog_model = create_tables(name_db=name_db, appeal_id=appeal_id)

    db.connect(reuse_if_open=True)

    # Получаем все записи
    messages = dialog_model.select().order_by(dialog_model.last_message_at.asc())

    result = []
    for message in messages:
        result.append({
            "user_id": message.user_id,
            "operator_id": message.operator_id,
            "message_text": message.message_text,
            "last_message_at": message.last_message_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

    return result
