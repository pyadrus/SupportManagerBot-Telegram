# -*- coding: utf-8 -*-
from aiogram import F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger

from src.bot.keyboards.keyboards import choose_lang, start
from src.bot.system.dispatcher import router
from src.core.database.database import register_user, set_user_lang


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
            "id": message.from_user.id, # ID пользователя
            "first_name": message.from_user.first_name, # Имя пользователя
            "last_name": message.from_user.last_name, # Фамилия пользователя
            "username": message.from_user.username, # Username пользователя
            "lang": 'ru', # Язык пользователя (Сделать проверку на наличие в базе данных)
            "date": message.date,  # Дата и время регистрации
        }
        # Записываем данные пользователя в базу данных src/core/database/database.db
        register_user(user_data)

        await message.answer(
            "👋 <b>Добро пожаловать! Выберите язык общения</b> / <b>Хуш омадед! Забони муомиларо интихоб кунед:</b>",
            reply_markup=choose_lang(), # Отправляем клавиатуру с выбором языка
        )
    except Exception as e:
        logger.error(f"Ошибка /start: {e} - {message.chat.id}")


@router.callback_query(F.data.startswith("lang-"))
async def choose_lang_handler(call: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор языка из меню выбора языка."""
    try:
        lang = call.data.split("-")[1]
        logger.info(f"Выбран язык {lang} - {call.from_user.id}")
        set_user_lang(call.from_user.id, lang)
        await call.message.edit_text(
            (
                "Чӣ тавр ман метавонам кӯмак кунам, сайёҳ? ✨"
                if lang == "tj"
                else "Чем могу помочь, путник? ✨"
            ),
            reply_markup=start(lang),
        )
    except Exception as e:
        logger.error(f"Ошибка выбора языка: {e} - {call.from_user.id}")
    finally:
        await state.clear()


def register_commands():
    router.message.register(cmd_start, CommandStart())
    router.callback_query.register(choose_lang_handler, F.data.startswith("lang-"))
