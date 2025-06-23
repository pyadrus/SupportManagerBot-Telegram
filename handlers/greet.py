# -*- coding: utf-8 -*-
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from loguru import logger

from dispatcher import router
from markups import choose_lang, admin_keyboard
from middlewares import AdminFilter


@router.message(CommandStart())
async def start(message: Message):
    """Отвечает на команду /start и выводит приветственное сообщение."""
    try:
        logger.info(f'Введена команда /start - {message.chat.id}')
        await message.answer(
            "👋 <b>Добро пожаловать! Выберите язык общения</b> / <b>Хуш омадед! Забони муомиларо интихоб кунед:</b>",
            reply_markup=choose_lang())
    except Exception as e:
        logger.error(f"Ошибка /start: {e} - {message.chat.id}")


@router.message(Command(commands=['admin']), AdminFilter())
async def admin(message: Message):
    try:
        logger.info(f'Введена команда /admin - {message.chat.id}')
        await message.answer(f"Здравствуйте, {message.from_user.first_name}! Вы попали в админ панель",
                             reply_markup=admin_keyboard())
    except Exception as e:
        logger.error(f"Ошибка /admin: {e} - {message.chat.id}")


def register_commands():
    router.message.register(start)
    router.message.register(admin)
