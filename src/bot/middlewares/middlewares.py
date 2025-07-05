# -*- coding: utf-8 -*-
from aiogram.filters import Filter
from aiogram.types import Message
from loguru import logger

from src.core.config.config import ADMIN
from src.core.database.database import get_user_status, check_manager_active_appeal, check_user_active_appeal


class AdminFilter(Filter):
    """Проверка на права админа"""

    async def __call__(self, message: Message) -> bool:
        try:
            return message.from_user.id == ADMIN
        except Exception as e:
            logger.exception(e)
            return False


# class UserStatusFilter(Filter):
#     """Проверка статуса пользователя"""
#     def __init__(self, allowed_statuses: list[str]):
#         self.allowed_statuses = allowed_statuses
#
#     async def __call__(self, message: Message) -> bool:
#         status = get_user_status(message.from_user.id)
#         return status in self.allowed_statuses

class ManagerAppealsFilter(Filter):
    """Проверка на наличие активных обращений менеджера"""

    async def __call__(self, message: Message) -> bool:
        try:
            return check_manager_active_appeal(message.from_user.id)
        except Exception as e:
            logger.exception(e)
            return False


class UserAppealsFilter(Filter):
    """Проверка на наличие активных обращений пользователя"""

    async def __call__(self, message: Message) -> bool:
        try:
            user_id = message.from_user.id
            has_appeal = check_user_active_appeal(user_id, status="в ожидании")
            logger.info(f"Пользователь {user_id} имеет активные обращения: {has_appeal}")
            return has_appeal
        except Exception as e:
            logger.exception(e)
            return False
