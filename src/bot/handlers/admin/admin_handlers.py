# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

from src.bot.keyboards.admin_keyboards import admin_keyboard
from src.bot.keyboards.user_keyboards import set_rating
from src.bot.middlewares.middlewares import AdminFilter, ManagerAppealsFilter, UserAppealsFilter
from src.bot.system.dispatcher import bot, router
from src.core.database.database import get_appeal, get_user_lang, update_appeal

close_timers = {}
# Константа для времени ожидания (например, 5 минут)
AUTO_CLOSE_DELAY = 20  # секунды


async def close_appeal_timeout(appeal_id: int, user_id: int, operator_id: int):
    """
    Задача, которая автоматически закрывает обращение после истечения времени

    :param appeal_id: ID обращения
    :param user_id: ID пользователя
    :param operator_id: ID оператора
    """
    try:
        logger.info(f"Запущен таймер для обращения #{appeal_id} (оператор: {operator_id}, пользователь: {user_id})")
        await asyncio.sleep(AUTO_CLOSE_DELAY)

        appeal = get_appeal(appeal_id=appeal_id)
        logger.info(f"Обращение для обращения #{appeal_id}: {appeal}")
        if not appeal or appeal.get("status") != "В обработке":
            logger.info(f"Таймер для обращения #{appeal_id} остановлен — статус: {appeal.get('status') if appeal else 'не найдено'}")
            return

        last_msg = appeal.get("last_message_at")
        if not last_msg:
            logger.warning(f"Время последнего сообщения для обращения #{appeal_id} отсутствует")
            return

        # Проверяем тип last_message_at
        if isinstance(last_msg, str):
            try:
                last_msg_dt = datetime.strptime(last_msg, "%d.%m.%Y %H:%M:%S")
            except ValueError as e:
                logger.error(f"Ошибка парсинга last_message_at для обращения #{appeal_id}: {last_msg}, ошибка: {e}")
                return
        else:
            last_msg_dt = last_msg  # Предполагаем, что это datetime объект

        elapsed = (datetime.now() - last_msg_dt).total_seconds()
        logger.info(f"Прошло времени с последнего сообщения для обращения #{appeal_id}: {elapsed} секунд")

        if elapsed >= AUTO_CLOSE_DELAY:
            update_appeal(
                appeal_id=appeal_id,
                status="Закрыто",
                operator_id=operator_id,
                last_message_at=datetime.now()
            )
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
                operator_id,
                f"<b>✅ Обращение закрыто</b>. Вы свободны для принятия новых заявок 👻",
            )
            logger.info(f"Автоматическое закрытие заявки #{appeal_id} по таймауту")
        else:
            logger.info(f"Обращение #{appeal_id} не закрыто: прошло {elapsed} секунд, требуется {AUTO_CLOSE_DELAY} секунд")

    except asyncio.CancelledError:
        logger.info(f"Таймер для обращения #{appeal_id} был отменён.")
        raise
    except Exception as e:
        logger.exception(f"Ошибка при автоматическом закрытии обращения #{appeal_id}: {e}")
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
        update_appeal(appeal_id=appeal["id"], status="Закрыто", operator_id=message.from_user.id,
                      last_message_at=datetime.now())
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
        if not appeal:  # Если обращение не найдено
            return  # Выходим из функции
        # Получаем ID пользователя, который отправил сообщение в бота
        await bot.send_message(appeal["user_id"], message.text)

        # Обновляем время последнего сообщения
        update_appeal(
            appeal_id=appeal["id"],  # id обращения
            status="В обработке",  # статус
            operator_id=message.from_user.id,  # id оператора
            last_message_at=datetime.now()  # время последнего сообщения
        )

        # Перезапускаем таймер
        await start_timer(appeal["id"], appeal["user_id"], message.from_user.id)
    except Exception as e:
        logger.exception(e)


@router.message(UserAppealsFilter(), F.text)
async def client_answer_appeal(message: Message):
    """Сообщения от пользователя, оператору"""
    try:
        logger.info(f"Ответ от клиента - {message.from_user.id}")
        # Получаем данные из базы данных к оператору
        appeal = get_appeal(user_id=message.from_user.id)
        logger.info(f"Обращение: {appeal}")
        if not appeal:  # Если обращение не найдено
            logger.warning(f"Обращение для пользователя {message.from_user.id} не найдено")
            return  # Выходим из функции
        # Получаем ID оператора из обращения
        operator_id = appeal["operator_id"]
        await bot.send_message(
            operator_id,
            f"🧑‍💻 Клиент:\n{message.text}"
        )
        # Обновляем время последнего сообщения
        update_appeal(
            appeal_id=appeal["id"],  # id обращения
            status="В обработке",  # статус
            operator_id=operator_id,  # id оператора
            last_message_at=datetime.now()  # время последнего сообщения
        )
        logger.info(f"Обновлено время последнего сообщения для обращения #{appeal['id']}")
        # Перезапускаем таймер
        await start_timer(appeal["id"], appeal["user_id"], operator_id)
        logger.info(f"Таймер запущен для обращения #{appeal['id']} с оператором {operator_id}")
    except Exception as e:
        logger.exception(e)


async def start_timer(appeal_id: int, user_id: int, operator_id: int):
    """Запуск нового таймера автоматического закрытия"""
    # Отменяем существующий таймер, если он есть
    await del_close_timer(appeal_id)
    # Создаём новый таймер
    task = asyncio.create_task(close_appeal_timeout(appeal_id, user_id, operator_id))
    close_timers[appeal_id] = task
    logger.info(f"Новый таймер создан для обращения #{appeal_id}")


async def del_close_timer(appeal_id: int):
    """Удаление и отмена таймера"""
    task = close_timers.get(appeal_id)
    if task:
        try:
            task.cancel()
            # Ждём завершения отмены задачи
            await asyncio.sleep(0)  # Даём шанс задаче обработать отмену
            logger.info(f"Таймер для обращения #{appeal_id} успешно отменён")
        except asyncio.CancelledError:
            logger.info(f"Таймер для обращения #{appeal_id} был в процессе отмены")
        finally:
            close_timers.pop(appeal_id, None)


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
    router.message.register(close_appeal_by_manager, F.text.in_(["❌ Закрыть заявку", "❌ Пӯшидани ариза"]))

    # --- Command handlers ---
    router.message.register(admin, Command(commands=["admin"]), AdminFilter())
