# -*- coding: utf-8 -*-
import re
from datetime import datetime
from typing import Optional

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger

from src.bot.keyboards.user_keyboards import close_appeal
from src.bot.system.dispatcher import bot, router
from src.core.database.database import (Appeal, check_manager_active_appeal,
                                        db, get_appeals,
                                        get_user_lang, update_appeal)


@router.callback_query(F.data == "accept_appeal")
async def accept_appeal(callback_query: CallbackQuery, state: FSMContext):
    """Принимает обращение от пользователя"""
    try:
        user_id = callback_query.from_user.id  # Получаем ID пользователя
        user_username = callback_query.from_user.username  # Получаем username пользователя
        text = callback_query.message.html_text  # Получаем текст сообщения

        db.connect()  # Подсоединяемся к базе данных
        db.create_tables([Appeal])  # Создаем таблицу, если она не существует

        if check_manager_active_appeal(user_id):  # Проверка на активное обращение
            await callback_query.answer(
                "У Вас есть активное обращение", show_alert=True
            )
            """
            Обращаемся к таблице Appeal проверяем есть ли в колонке manager_id значение None, то
            берем id оператора и вписываем его в колонку manager_id, в колонку status_id вписываем 2
            Статусы:
            В ожидании
            В обработке
            Закрыто
            """
        else:
            appeal_id = extract_appeal_id(text)
            logger.info(f" Запрос принятия обращения от {appeal_id}")
            if appeal_id:
                appeal = get_appeals(appeal_id=appeal_id)
                logger.info(f"Принято обращение #{appeal_id} от {user_id}. {appeal}")

                if appeal["user_id"] == user_id:
                    await callback_query.answer(
                        "Вы не можете принять свою заявку", True
                    )
                    return
                await callback_query.message.edit_text(
                    f"{text}\n\n🔥 Заявка принята {f'@{user_username}' if user_username else f'<code>{user_id}</code>'}\n🕛 Дата принятия: <code>{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</code>"
                )
                await bot.send_message(
                    user_id,
                    f"Вы приняли заявку:\n{text}",
                    reply_markup=close_appeal(appeal_id),
                )
                client_lang = get_user_lang(appeal["user_id"])
                await bot.send_message(
                    appeal["user_id"],
                    (
                        "🤝 <b>Мутахассис ба дархости шумо пайваст шуд.</b> Шумо метавонед оғоз кунед ✨"
                        if client_lang == "tj"
                        else "🤝 <b>Специалист подключился к вашему запросу.</b> Можете начать общение ✨"
                    ),
                )
                update_appeal(appeal_id=appeal_id, status="В обработке", operator_id=user_id)
            else:
                await callback_query.message.edit_text("В обращении не найден id")
    except Exception as e:
        logger.exception(e)
    finally:
        await state.clear()


def extract_appeal_id(text: str) -> Optional[int]:
    """Извлекает ID обращения из текста"""
    try:
        match = re.search(r"🆔\s*<code>#(\d+)</code>", text)
        if match:
            return int(match.group(1))
    except Exception as e:
        print(f"Ошибка при извлечении ID: {e}")


def register_manager_handlers_group():
    router.callback_query.register(accept_appeal, F.data == "accept_appeal")
