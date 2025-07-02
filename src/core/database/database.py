# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Union

from loguru import logger
from peewee import *  # https://docs.peewee-orm.com/en/latest/index.html

from src.core.config.config import DB_NAME

# Настраиваем синхронную базу данных SQLite
db = SqliteDatabase(f"src/core/database/{DB_NAME}")

"""Работа с выдачей прав операторам"""


class User(Model):
    user_id = IntegerField(primary_key=True)
    lang = CharField(null=True)

    class Meta:
        database = db


"""Работа с базой данных"""


class Status(Model):
    status = CharField(unique=True)

    class Meta:
        database = db


class Appeal(Model):
    user = ForeignKeyField(User, backref="appeals")  # Кто создал обращение
    manager = ForeignKeyField(User, null=True, backref="managed_appeals")  # Кто обрабатывает
    status = ForeignKeyField(Status, backref="tickets", default=1)  # Статус
    rating = IntegerField(null=True)  # Оценка
    last_message_at = DateTimeField(default=datetime.now)  # Время последнего сообщенияs

    class Meta:
        database = db


def get_status_name(status_id: int) -> str:
    """Получает название статуса по его ID"""
    try:
        with db:
            status = Status.select().where(Status.id == status_id).get_or_none()
            return status.status if status else ""
    except Exception as e:
        logger.error(f"Ошибка получения названия статуса {status_id}: {e}")
        return ""


def create_appeal(user_id: int, status_id: int = 1) -> int:
    """Создаёт обращение для пользователя"""
    try:
        with db:
            status = Status.select().where(Status.id == status_id).get_or_none()
            if not status:
                status = Status.select().where(Status.status == "В ожидании").get()

            appeal = Appeal.create(user=user_id, status=status)
            return appeal.id
    except Exception as e:
        logger.error(f"Ошибка создания обращения для пользователя {user_id}: {e}")
        return 0


def get_appeal(**kwargs) -> Union[dict, list[dict]]:
    """Получает обращение по фильтрам"""
    try:
        with db:
            query = Appeal.select()
            for key, value in kwargs.items():
                field = getattr(Appeal, key)
                query = query.where(field == value)

            # Собираем результаты в список словарей вручную
            result = []
            for appeal in query:
                appeal_dict = {
                    "id": appeal.id,
                    "user_id": appeal.user.user_id_operator if appeal.user else None,
                    "manager_id": appeal.manager.user_id_operator if appeal.manager else None,
                    "status_id": appeal.status.id if appeal.status else None,
                    "rating": appeal.rating,
                    "last_message_at": appeal.last_message_at,
                }
                result.append(appeal_dict)

            return result if len(result) > 1 else result[0] if result else {}
    except Exception as e:
        logger.error(f"Ошибка получения обращения: {e}")
        return {}


def update_appeal(appeal_id: int, **kwargs):
    """Обновляет обращение"""
    try:
        with db:
            Appeal.update(**kwargs).where(Appeal.id == appeal_id).execute()
    except Exception as e:
        logger.error(f"Ошибка обновления обращения {appeal_id}: {e}")


def check_user_active_appeal(user_id: int) -> bool:
    """Проверяет, есть ли у пользователя активное обращение"""
    try:
        with db:
            count = (
                Appeal.select()
                .where(Appeal.user == user_id, Appeal.status.in_([1, 2]))
                .count()
            )
            return count > 0
    except Exception as e:
        logger.error(f"Ошибка проверки активных обращений пользователя {user_id}: {e}")
        return False


def check_manager_active_appeal(manager_id: int) -> bool:
    """Проверяет, есть ли у менеджера активное обращение"""
    try:
        with db:
            count = (
                Appeal.select()
                .where(Appeal.manager == manager_id, Appeal.status.in_([1, 2]))
                .count()
            )
            return count > 0
    except Exception as e:
        logger.error(f"Ошибка проверки активных обращений менеджера {manager_id}: {e}")
        return False


"""Запись в базу данных пользователей, запустивших бота вызвав команду /start."""


class Person(Model):
    """
    Хранит информацию о пользователях, запустивших Telegram-бота вызвав команду /start.
    """

    id_user = IntegerField(unique=True)  # Telegram ID пользователя Telegram (unique=True - уникальный ID)
    first_name = CharField(null=True)  # Telegram Имя пользователя
    last_name = CharField(null=True)  # Telegram Фамилия пользователя
    username_tg = CharField(null=True)  # Telegram username
    lang = CharField(null=True)  # Язык пользователя
    status = CharField(null=True)  # Статус пользователя (operator, admin, user)
    username = CharField(null=True)  # Username, 'operator', 'admin'
    password = CharField(null=True)  # Password для веб-авторизации
    created_at = DateTimeField()  # Время запуска

    class Meta:  # Подключение к базе данных
        database = db  # Модель базы данных
        table_name = "registered_users"  # Имя таблицы


def register_user(user_data) -> None:
    """
    Записывает данные пользователя в базу данных, который вызвал команду /start.

    :param user_data: Словарь с данными пользователя, для последующей записи в БД src/core/database/database.db
    """
    db.connect()  # Подсоединяемся к базе данных
    db.create_tables([Person])  # Создаем таблицу, если она не существует

    Person.get_or_create(
        id_user=user_data["id"],  # Telegram ID пользователя Telegram
        defaults={
            "first_name": user_data.get("first_name"),  # Telegram Имя пользователя
            "last_name": user_data.get("last_name"),  # Telegram Фамилия пользователя
            "username_tg": user_data.get("username_tg"),  # Telegram username
            "lang": user_data.get("lang"),  # Язык пользователя
            "status": user_data.get("status"),  # Статус пользователя (operator, admin, user)
            "username": user_data.get("username"),  # Username, 'operator', 'admin'
            "password": user_data.get("password"),  # Password для веб-авторизации
            "created_at": user_data.get("date"),  # Время запуска
        }
    )


"""Чтение данных из базы данных, для проверки данных внесенных админом Telegram бота"""


def get_all_authorization_data():
    """Получение всех данных из базы данных"""
    db.connect()  # Подключаемся к базе данных
    data = []  # Создаем пустой список для хранения данных
    for entry in Person.select():
        data.append(
            {
                "id": entry.id,
                "username": entry.username,
                "password": entry.password,
                "created_at": entry.created_at,
            }
        )
    db.close()  # Закрываем соединение с базой данных
    return data  # Возвращаем список данных


"""Выдача роль операторам, администраторам для авторизации в веб-интерфейсе"""


def set_user_role(id_user, status, username, password):
    """
    Устанавливает или обновляет роль пользователя.
    :param id_user: ID пользователя в Telegram, которому устанавливается роль и выдается пароль.
    :param status: Статус пользователя, который устанавливается (operator, admin).
    :param username: Username, 'operator', 'admin' для авторизации в веб-интерфейсе.
    :param password: Пароль для авторизации в веб-интерфейсе.
    """
    with db:
        query = Person.update(
            {
                Person.status: status,  # Статус пользователя (operator, admin)
                Person.username: username,  # Username для авторизации в веб-интерфейсе
                Person.password: password  # Пароль для авторизации в веб-интерфейсе
            }
        ).where(Person.id_user == id_user)
        query.execute()


"""Установка языка пользователя"""


def set_user_lang(id_user: int, lang: str):
    """Обновляет язык пользователя по Telegram ID"""
    with db:
        query = Person.update({Person.lang: lang}).where(Person.id_user == id_user)
        query.execute()


"""Получение языка пользователя"""


def get_user_lang(id_user: int) -> str | None:
    """Возвращает язык пользователя по Telegram ID. Если пользователь не найден — None."""
    with db:
        user = Person.get_or_none(Person.id_user == id_user)
        return user.lang if user else None


"""Получение статуса пользователя зарегистрированного в Telegram боте"""
def get_user_status(id_user: int) -> str | None:
    """Возвращает статус пользователя по Telegram ID. Если пользователь не найден — None."""
    with db:
        status = Person.get_or_none(Person.id_user == id_user)
        return status.status if status else None