# -*- coding: utf-8 -*-
from aiogram.filters import Filter
from aiogram.types import Message

from src.core.config.config import ADMIN
from src.core.database.database import db
from loguru import logger


class AdminFilter(Filter):
    """Проверка на права админа"""

    async def __call__(self, message: Message) -> bool:
        try:
            return True if message.from_user.id == ADMIN else False
        except Exception as e:
            logger.exception(e)


class ManagerAppealsFilter(Filter):
    """Проверка на наличие активных обращений"""

    async def __call__(self, message: Message) -> bool:
        try:
            return await db.check_manager_active_appeal(message.from_user.id)
        except Exception as e:
            logger.exception(e)


class UserAppealsFilter(Filter):
    """Проверка на наличие активных обращений"""

    async def __call__(self, message: Message) -> bool:
        try:
            return await db.check_user_active_appeal(message.from_user.id)
        except Exception as e:
            logger.exception(e)
