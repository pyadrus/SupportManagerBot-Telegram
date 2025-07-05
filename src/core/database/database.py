# -*- coding: utf-8 -*-
from datetime import datetime

from loguru import logger
from peewee import *  # https://docs.peewee-orm.com/en/latest/index.html

from src.core.config.config import DB_NAME

# Настраиваем синхронную базу данных SQLite
db = SqliteDatabase(f"src/core/database/{DB_NAME}")

"""Работа с выдачей прав операторам"""

"""Работа с базой данных"""


class Appeal(Model):
    user_id = CharField(null=True)  # Кто создал обращение (ID Telegram пользователя)
    operator_id = CharField(null=True)  # Кто обрабатывает (ID Telegram оператора)
    status = CharField(null=True)  # Статус
    rating = IntegerField(null=True)  # Оценка
    last_message_at = DateTimeField(default=datetime.now)  # Время последнего сообщения
    user_question = CharField(null=True)  # Вопрос пользователя
    full_name = CharField(null=True)  # Полное имя пользователя (Имя + Фамилия + Отчество)
    phone = CharField(null=True)  # Номер телефона пользователя

    class Meta:
        database = db
        table_name = "appeals"


"""Записываем данные обращения в базу данных, таблицу appeals."""


def create_appeal(user_id, operator_id, status, rating, last_message_at, user_question, full_name, phone):
    """Создаёт обращение для пользователя"""
    db.connect()  # Подсоединяемся к базе данных
    db.create_tables([Appeal])  # Создаем таблицу, если она не существует

    # Получаем или создаём запись
    appeal, created = Appeal.get_or_create(
        user_id=user_id,  # Telegram ID пользователя Telegram
        operator_id=operator_id,
        # Telegram ID оператора (При первом обращении оператор не присваивается, а присваивается None)
        status=status,  # Статус обращения (В ожидании, Обрабатывается, Закрыто)
        rating=rating,  # Присваивается в начале None, так как при первой записи, рейтинга нет
        last_message_at=last_message_at,  # Время последнего сообщения
        user_question=user_question,  # Вопрос пользователя
        full_name=full_name,  # Полное имя пользователя (Имя + Фамилия + Отчество)
        phone=phone,  # Номер телефона пользователя
    )
    db.close()  # Закрываем соединение с базой данных
    # Возвращаем ID созданной (или существующей) записи
    return appeal.id  # <-- ID из базы данных


def check_user_active_appeal(user_id, status) -> bool:
    """
    Проверяет, есть ли у пользователя активное обращение

    :param user_id: ID пользователя Telegram
    :param status: Статус обращения (в ожидании, обрабатывается, закрыто)
    """
    with db:
        # Получаем количество записей с заданным статусом у пользователя
        count = Appeal.select().where(
            Appeal.user_id == str(user_id),
            Appeal.status == status
        ).count()

        return count > 0  # Если больше нуля, то возвращаем True, иначе False


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
        },
    )


"""Проверка, есть ли у оператора активное обращение"""


def check_manager_active_appeal(operator_id: int) -> bool:
    """Проверяет, есть ли у оператора активное обращение"""
    try:
        with db:
            count = (
                Appeal.select()
                .where(
                    Appeal.operator_id == str(operator_id),
                    Appeal.status.in_(("В ожидании", "В обработке"))
                )
                .count()
            )
            return count > 0
    except Exception as e:
        logger.exception(f"Ошибка проверки активных обращений менеджера {operator_id}: {e}")
        return False


"""Установка языка пользователя"""


def set_user_lang(id_user: int, lang: str):
    """Обновляет язык пользователя по Telegram ID"""
    with db:
        query = Person.update({Person.lang: lang}).where(Person.id_user == id_user)
        query.execute()


"""Обновление обращения на статус В обработке"""


def update_appeal(appeal_id: int, status: str, operator_id: int):
    """Обновляет обращение"""
    try:
        with db:
            Appeal.update({Appeal.status: status, Appeal.operator_id: operator_id}).where(Appeal.id == appeal_id).execute()
            # update_appeal.execute()
    except Exception as e:
        logger.exception(f"Ошибка обновления обращения {appeal_id}: {e}")


"""Получение языка пользователя"""


def get_user_lang(id_user: int) -> str | None:
    """Возвращает язык пользователя по Telegram ID. Если пользователь не найден — None."""
    with db:
        user = Person.get_or_none(Person.id_user == id_user)
        return user.lang if user else None


def get_appeal(user_id=None, operator_id=None, status="В обработке"):
    """Получает активное обращение по user_id или operator_id"""
    try:
        with db:
            query = Appeal.select().where(Appeal.status == status)
            if user_id:
                query = query.where(Appeal.user_id == str(user_id))
            elif operator_id:
                query = query.where(Appeal.operator_id == str(operator_id))

            appeal = query.first()
            if not appeal:
                return None

            return {
                "id": appeal.id,
                "user_id": appeal.user_id,
                "operator_id": appeal.operator_id,
                "status": appeal.status,
                "rating": appeal.rating,
                "last_message_at": appeal.last_message_at,
                "user_question": appeal.user_question,
                "full_name": appeal.full_name,
                "phone": appeal.phone,
            }
    except Exception as e:
        logger.exception(f"Ошибка получения обращения: {e}")
        return None


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
                Person.password: password,  # Пароль для авторизации в веб-интерфейсе
            }
        ).where(Person.id_user == id_user)
        query.execute()


"""Записываем ID оператора в базу данных, для отметки менеджера, который обрабатывает обращение от пользователя"""


def set_operator_id(id_user: int, status_id: int):
    """Меняем статус обработки обращения и записываем ID оператора, который обрабатывает обращение от пользователя"""
    with db:
        query = Appeal.update(
            {
                Appeal.status_id: status_id,
            }
        ).where(Appeal.id_user == id_user)
        query.execute()


"""Получение статуса пользователя зарегистрированного в Telegram боте"""


def get_user_status(id_user: int) -> str | None:
    """Возвращает статус пользователя по Telegram ID. Если пользователь не найден — None."""
    with db:
        status = Person.get_or_none(Person.id_user == id_user)
        return status.status if status else None


"""Получаем ID оператора по статусу. Возвращаем список ID операторов [123456789, 987654321, ...]."""


def get_operator_ids_by_status(status: str):
    """Получаем список ID операторов по статусу"""
    with db:
        operators = Person.select().where(Person.status == status)
        return [operator.id_user for operator in operators]

# def get_status_name(status_id: int) -> str:
# """Получает название статуса по его ID"""
# try:
# with db:
# status = Status.select().where(Status.id == status_id).get_or_none()
# return status.status if status else ""
# except Exception as e:
# logger.error(f"Ошибка получения названия статуса {status_id}: {e}")
# return ""
