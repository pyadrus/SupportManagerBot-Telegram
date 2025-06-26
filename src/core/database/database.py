# -*- coding: utf-8 -*-
from datetime import datetime
from typing import Optional, Union
from loguru import logger
from peewee import *

from src.core.config.config import DB_NAME

# Настраиваем синхронную базу данных SQLite
db = SqliteDatabase(f"src/core/database/{DB_NAME}")


class BaseModel(Model):
    class Meta:
        database = db


class Person(BaseModel):
    """
    Хранит информацию о пользователях, запустивших Telegram-бота.
    """
    id_user = IntegerField(unique=True)  # Уникальный ID пользователя Telegram
    first_name = CharField(null=True)  # Имя пользователя
    last_name = CharField(null=True)  # Фамилия пользователя
    username = CharField(null=True)  # Telegram username
    created_at = DateTimeField()  # Время запуска

    class Meta:
        table_name = "registered_users_start"


class User(BaseModel):
    user_id = IntegerField(primary_key=True)
    lang = CharField(null=True)  # Язык пользователя


class Status(BaseModel):
    status = CharField(unique=True)


class Appeal(BaseModel):
    user = ForeignKeyField(User, backref="appeals")  # Кто создал обращение
    manager = ForeignKeyField(User, null=True, backref="managed_appeals")  # Кто обрабатывает
    status = ForeignKeyField(Status, backref="tickets", default=1)  # Статус
    rating = IntegerField(null=True)  # Оценка
    last_message_at = DateTimeField(default=datetime.now)  # Время последнего сообщенияs


def register_user(user_data):
    """Регистрирует пользователя в БД на основе переданных данных"""
    with db:
        Person.get_or_create(
            id_user=user_data["id"],
            defaults={
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "username": user_data["username"],
                "created_at": user_data["date"]
            }
        )
        User.get_or_create(
            user_id=user_data["id"],
            defaults={"lang": user_data.get("lang", None)}
        )


def set_user_lang(user_id: int, lang: str):
    """Устанавливает язык для пользователя"""
    with db:
        User.insert(user_id=user_id, lang=lang).on_conflict(
            conflict_target=[User.user_id],
            preserve=[User.lang]
        ).execute()


def get_user_lang(user_id: int) -> Optional[str]:
    """Получает язык пользователя"""
    try:
        with db:
            user = User.select().where(User.user_id == user_id).get_or_none()
            return user.lang if user else None
    except Exception as e:
        logger.error(f"Ошибка получения языка пользователя {user_id}: {e}")
        return None


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
                    "user_id": appeal.user.user_id if appeal.user else None,
                    "manager_id": appeal.manager.user_id if appeal.manager else None,
                    "status_id": appeal.status.id if appeal.status else None,
                    "rating": appeal.rating,
                    "last_message_at": appeal.last_message_at
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
            count = Appeal.select().where(
                Appeal.user == user_id,
                Appeal.status.in_([1, 2])
            ).count()
            return count > 0
    except Exception as e:
        logger.error(f"Ошибка проверки активных обращений пользователя {user_id}: {e}")
        return False


def check_manager_active_appeal(manager_id: int) -> bool:
    """Проверяет, есть ли у менеджера активное обращение"""
    try:
        with db:
            count = Appeal.select().where(
                Appeal.manager == manager_id,
                Appeal.status.in_([1, 2])
            ).count()
            return count > 0
    except Exception as e:
        logger.error(f"Ошибка проверки активных обращений менеджера {manager_id}: {e}")
        return False
