# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime, timedelta

from aiogram import F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from loguru import logger

from src.bot.keyboards.admin_keyboards import admin_keyboard
from src.bot.keyboards.user_keyboards import set_rating, stat_period
from src.bot.middlewares.middlewares import (AdminFilter, ManagerAppealsFilter,
                                             UserAppealsFilter)
from src.bot.system.dispatcher import bot, router
from src.core.database.database import get_appeal, get_user_lang, update_appeal

close_timers = {}
# Константа для времени ожидания (например, 5 минут)
AUTO_CLOSE_DELAY = 300  # секунды


async def close_appeal_timeout(appeal_id: int, user_id: int, manager_id: int):
    """Задача, которая автоматически закрывает обращение после истечения времени"""
    try:
        await asyncio.sleep(AUTO_CLOSE_DELAY)

        # Проверяем, не был ли таймер отменён ранее
        if close_timers.get(appeal_id) is not asyncio.current_task():
            return

        appeal = get_appeal(id=appeal_id)
        if not appeal or appeal.get("status_id") != 2:
            logger.info(f"Таймер для обращения {appeal_id} остановлен — статус изменён")
            return

        last_msg_str = appeal.get("last_message_at")
        if not last_msg_str:
            return

        # Проверяем тип даты
        if isinstance(last_msg_str, str):
            last_msg_dt = datetime.strptime(last_msg_str, "%d.%m.%Y %H:%M:%S")
        else:
            last_msg_dt = last_msg_str  # Если это datetime объект

        elapsed = (datetime.now() - last_msg_dt).total_seconds()

        if elapsed >= AUTO_CLOSE_DELAY:
            update_appeal(appeal_id, status_id=3)
            lang = get_user_lang(user_id)

            await bot.send_message(
                user_id,
                (
                    "Лутфан сифати хидматро арзебӣ кунед, то мо беҳтар шавем"
                    if lang == "tj"
                    else "Пожалуйста, оцените качество обслуживания, чтобы мы могли стать лучше ✨"
                ),
                reply_markup=set_rating(appeal_id),
            )
            await bot.send_message(
                manager_id,
                f"<b>✅ Обращение закрыто</b>. Вы свободны для принятия новых заявок 👻",
            )
            logger.info(f"Автоматическое закрытие заявки #{appeal_id} по таймауту")

    except asyncio.CancelledError:
        logger.info(f"Таймер для обращения {appeal_id} был отменен.")
        raise
    except Exception as e:
        logger.exception(
            f"Ошибка при автоматическом закрытии обращения {appeal_id}: {e}"
        )
    finally:
        close_timers.pop(appeal_id, None)


@router.message(F.text.in_(["❌ Закрыть заявку", "❌ Пӯшидани ариза"]))
async def close_appeal_by_manager(message: Message):
    try:
        appeal = get_appeal(operator_id=message.from_user.id, status="В обработке")
        logger.info(appeal)

        if not appeal:
            await message.answer("Заявка не найдена")
            return
        await del_close_timer(appeal["id"])
        update_appeal(
            appeal_id=appeal["id"], status="Закрыто", operator_id=message.from_user.id
        )
        lang_client = get_user_lang(appeal["user_id"])
        await bot.send_message(
            appeal["user_id"],
            (
                "Оператор сӯҳбатро анҷом дод. Ташаккур барои муроҷиат! Лутфан, сифати хизматрасониро баҳо диҳед, то мо беҳтар шавем. ✨"
                if lang_client == "tj"
                else "Оператор завершил чат. Спасибо за обращение! Пожалуйста, оцените качество обслуживания, чтобы мы могли стать лучше. ✨"
            ),
            reply_markup=set_rating(appeal["id"]),
        )
        await message.answer(
            f"✅ <b>Вы завершили чат</b> Вы свободны для принятия новых заявок 👻"
        )
        logger.info(f"Закрытие обращения - {message.from_user.id}")
    except Exception as e:
        logger.exception(e)
        # await message.answer("Произошла ошибка при закрытии заявки")


@router.message(ManagerAppealsFilter(), F.text)
async def manager_answer_appeal(message: Message):
    """Сообщения от операторов, администраторов"""
    try:
        logger.info(f"Сообщение от оператора - {message.from_user.id}")
        # Получаем данные из базы данных к оператору
        appeal = get_appeal(operator_id=message.from_user.id)
        logger.info(appeal)
        # Получаем ID пользователя, который отправил сообщение в бота
        await bot.send_message(appeal["user_id"], message.text)
        # Перезапускаем таймер
        await start_timer(appeal["id"], appeal["user_id"], message.from_user.id)
    except Exception as e:
        logger.exception(e)


async def start_timer(appeal_id: int, user_id: int, manager_id: int):
    """Запуск нового таймера автоматического закрытия"""
    if appeal_id in close_timers:
        close_timers[appeal_id].cancel()
    task = asyncio.create_task(close_appeal_timeout(appeal_id, user_id, manager_id))
    close_timers[appeal_id] = task


async def del_close_timer(appeal_id: int):
    """Удаление и отмена таймера"""
    task = close_timers.pop(appeal_id, None)
    if task:
        task.cancel()


@router.message(UserAppealsFilter(), F.text)
async def client_answer_appeal(message: Message):
    """Сообщения от пользователя, оператору"""
    try:
        logger.info(f"Ответ от клиента - {message.from_user.id}")
        # appeal = get_appeal(user_id=message.from_user.id)
        #
        # if appeal and isinstance(appeal, dict):
        #     if appeal["operator_id"]:
        #         await bot.send_message(appeal["operator_id"], f"🧑‍💻 Клиент:\n{message.text}")
        #         update_appeal(
        #             appeal["id"],
        #             last_message_at=datetime.now()
        #         )
        # await start_timer(appeal["id"], appeal["user_id"], appeal["operator_id"])
        # else:
        #     await message.answer("Ожидайте подключения оператора...")
        # else:
        #     await message.answer("Обращение не найдено.")
    except Exception as e:
        logger.exception(e)
        # logger.error(f"Ошибка ответа от клиента: {e} - {message.from_user.id}")
        # await message.answer("Произошла ошибка, попробуйте ещё раз")


@router.message(Command(commands=["admin"]), AdminFilter())
async def admin(message: Message):
    """Выводит админ панель."""
    try:
        logger.info(f"Введена команда /admin - {message.chat.id}")
        await message.answer(
            f"Здравствуйте, {message.from_user.first_name}! Вы попали в админ панель",
            reply_markup=admin_keyboard(),
        )
    except Exception as e:
        logger.error(f"Ошибка /admin: {e} - {message.chat.id}")


def register_handlers_admin():
    # --- Callback handlers ---
    router.callback_query.register(
        close_appeal_by_manager, F.data == "close_appeal_by_manager"
    )  # Если есть такая кнопка
    router.callback_query.register(set_rating, F.data.startswith("set_rating-"))

    # --- Message handlers (текстовые сообщения) ---
    router.message.register(manager_answer_appeal, F.text)
    router.message.register(client_answer_appeal, F.text)
    router.message.register(
        close_appeal_by_manager, F.text.in_(["❌ Закрыть заявку", "❌ Пӯшидани ариза"])
    )

    # --- Command handlers ---
    router.message.register(admin, Command(commands=["admin"]), AdminFilter())
