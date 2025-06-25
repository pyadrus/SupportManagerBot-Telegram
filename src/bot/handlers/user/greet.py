# -*- coding: utf-8 -*-
from aiogram import F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from src.bot.keyboards.keyboards import choose_lang, start, admin_keyboard
from src.bot.middlewares.middlewares import AdminFilter
from src.bot.system.dispatcher import router
from src.core.database.database import register_user, set_user_lang


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Отвечает на команду /start и выводит приветственное сообщение."""
    try:
        logger.info(f'Введена команда /start - {message.chat.id}')

        # Формируем данные пользователя
        user_data = {
            "id": message.from_user.id,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "username": message.from_user.username,
            "chat_id": str(message.chat.id),  # chat.id как строка
            "date": message.date  # DateTime object from aiogram
        }

        register_user(user_data)

        await message.answer(
            "👋 <b>Добро пожаловать! Выберите язык общения</b> / <b>Хуш омадед! Забони муомиларо интихоб кунед:</b>",
            reply_markup=choose_lang()
        )
    except Exception as e:
        logger.error(f"Ошибка /start: {e} - {message.chat.id}")


@router.callback_query(F.data.startswith("lang-"))
async def choose_lang_handler(call: CallbackQuery, state: FSMContext):
    """Обрабатывает выбор языка из меню выбора языка."""
    try:
        lang = call.data.split('-')[1]
        logger.info(f'Выбран язык {lang} - {call.from_user.id}')
        set_user_lang(call.from_user.id, lang)
        await call.message.edit_text(
            "Чӣ тавр ман метавонам кӯмак кунам, сайёҳ? ✨" if lang == 'tj' else "Чем могу помочь, путник? ✨",
            reply_markup=start(lang))
    except Exception as e:
        logger.error(f"Ошибка выбора языка: {e} - {call.from_user.id}")
    finally:
        await state.clear()


@router.message(Command(commands=['admin']), AdminFilter())
async def admin(message: Message):
    try:
        logger.info(f'Введена команда /admin - {message.chat.id}')
        await message.answer(f"Здравствуйте, {message.from_user.first_name}! Вы попали в админ панель",
                             reply_markup=admin_keyboard())
    except Exception as e:
        logger.error(f"Ошибка /admin: {e} - {message.chat.id}")


def register_commands():
    router.message.register(cmd_start, CommandStart())
    router.message.register(admin, Command(commands=['admin']), AdminFilter())
    router.callback_query.register(choose_lang_handler, F.data.startswith("lang-"))