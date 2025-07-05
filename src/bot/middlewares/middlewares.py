# -*- coding: utf-8 -*-
from aiogram.filters import Filter
from aiogram.types import Message
from loguru import logger

from src.core.config.config import ADMIN


class AdminFilter(Filter):
    """Проверка на права админа"""

    async def __call__(self, message: Message) -> bool:
        try:
            return message.from_user.id == ADMIN
        except Exception as e:
            logger.exception(e)
            return False

# class ManagerAppealsFilter(Filter):
#     """Проверка на наличие активных обращений менеджера"""

#     async def __call__(self, message: Message) -> bool:
#         try:
#             return check_manager_active_appeal(message.from_user.id)
#         except Exception as e:
#             logger.exception(e)
#             return False


# class UserAppealsFilter(Filter):
#     """Проверка на наличие активных обращений пользователя"""

#     async def __call__(self, message: Message) -> bool:
#         try:
#             return check_user_active_appeal(message.from_user.id)
#         except Exception as e:
#             logger.exception(e)
#             return False
