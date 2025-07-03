# -*- coding: utf-8 -*-
from aiogram import F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from loguru import logger

from src.bot.keyboards.admin_keyboards import admin_keyboard
from src.bot.keyboards.operator_keyboards import operator_keyboard
from src.bot.keyboards.user_keyboards import choose_lang, start
from src.bot.system.dispatcher import bot, router
from src.core.database.database import (get_user_status, register_user,
                                        set_user_lang)


@router.message(CommandStart())
async def cmd_start(message: Message):
    """
    Отвечает на команду /start и выводит приветственное сообщение пользователю. Записывает в базу данных
    src/core/database/database.db, данные пользователя, который ввел команду /start.
    """
    try:
        logger.info(f"Введена команда /start - {message.chat.id}")

        # Формируем данные пользователя
        user_data = {
            "id": message.from_user.id,  # ID пользователя
            "first_name": message.from_user.first_name,  # Имя пользователя
            "last_name": message.from_user.last_name,  # Фамилия пользователя
            "username_tg": message.from_user.username,  # Username пользователя
            "lang": 'ru',  # Язык пользователя (Сделать проверку на наличие в базе данных)
            "status": 'user',  # Статус пользователя (Admin, operator, user)
            "username": 'user',  # 'user', 'operator', 'admin'
            "password": None,  # Пароль пользователя
            "date": message.date,  # Дата и время регистрации
        }
        # Записываем данные пользователя в базу данных src/core/database/database.db
        register_user(user_data)

        # Проверяем статус пользователя из базы данных src/core/database/database.db
        status = get_user_status(message.from_user.id)
        logger.info(f"Статус пользователя {status}")

        if status == 'admin':  # Проверяем статус пользователя
            logger.info(f"Пользователь {message.from_user.id} администратор")
            await message.answer(
                f"Здравствуйте, {message.from_user.first_name}! Вы попали в админ панель",
                reply_markup=admin_keyboard()
            )
            return

        if status == 'operator':  # Проверяем статус пользователя
            logger.info(f"Пользователь {message.from_user.id} оператор")
            await message.answer(
                f"Здравствуйте, {message.from_user.first_name}! Вы попали в панель оператора",
                reply_markup=operator_keyboard()
            )
            return

        if status == 'user':  # Проверяем статус пользователя
            logger.info(f"Пользователь {message.from_user.id} пользователь")
            await message.answer(
                "👋 <b>Добро пожаловать! Выберите язык общения</b> / <b>Хуш омадед! Забони муомиларо интихоб кунед:</b>",
                reply_markup=choose_lang(),  # Отправляем клавиатуру с выбором языка
            )
            return

    except Exception as e:
        logger.error(f"Ошибка /start: {e} - {message.chat.id}")


@router.callback_query(F.data.startswith("lang-"))
async def choose_lang_handler(callback_query: CallbackQuery):
    """Обрабатывает выбор языка из меню выбора языка."""
    lang = callback_query.data.split("-")[1]
    logger.info(f"Выбран язык {lang} - {callback_query.from_user.id}")
    set_user_lang(callback_query.from_user.id, lang)
    await bot.send_message(
        chat_id=callback_query.from_user.id,
        text=(
            "Чӣ тавр ман метавонам кӯмак кунам, сайёҳ? ✨"
            if lang == "tj"
            else "Чем могу помочь, путник? ✨"
        ),
        reply_markup=start(lang),
    )


def register_commands():
    router.message.register(cmd_start, CommandStart())
    router.callback_query.register(choose_lang_handler, F.data.startswith("lang-"))
