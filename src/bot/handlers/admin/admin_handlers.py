# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime, timedelta

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from loguru import logger

from src.bot.keyboards.admin_keyboards import admin_keyboard
from src.bot.keyboards.user_keyboards import set_rating, stat_period
from src.bot.middlewares.middlewares import (
    AdminFilter,
    # ManagerAppealsFilter,
    # UserAppealsFilter,
)
from src.bot.system.dispatcher import bot, router
from src.core.database.database import (
    # get_appeal,
    update_appeal,
    get_user_lang,
)

close_timers = {}


async def close_appeal_timeout(
        appeal_id: int, user_id: int, manager_id: int, timeout_seconds=30
):
    try:
        while True:
            await asyncio.sleep(5)
            # appeal = get_appeal(id=appeal_id)
            appeal = None
            if not appeal or appeal.get("status_id") != 2:
                logger.info(f"Таймер закрытия для заявки #{appeal_id} остановлен")
                break

            last_msg_str = appeal.get("last_message_at")
            if not last_msg_str:
                continue

            last_msg_dt = datetime.strptime(last_msg_str, "%d.%m.%Y %H:%M:%S")
            elapsed = (datetime.now() - last_msg_dt).total_seconds()

            if elapsed >= timeout_seconds:
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
                break
    except Exception as e:
        logger.error(f"Ошибка таймера закрытия заявки #{appeal_id}: {e}")
    finally:
        close_timers.pop(appeal_id, None)


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


@router.callback_query(F.data == "statistic", AdminFilter())
async def ask_period(call: CallbackQuery):
    """Запрос на выбор периода статистики"""
    await call.message.edit_text(
        "Выберите период для статистики:", reply_markup=stat_period()
    )


@router.callback_query(F.data.startswith("statistic-"))
async def statistics(call: CallbackQuery):
    try:
        period = call.data.split("-")[1]

        now = datetime.now()
        from_date = now - timedelta(days=int(period))

        logger.info(f"Статистика за {period} - {call.from_user.id}")

        appeals_raw = None
        # appeals_raw = get_appeal()

        if isinstance(appeals_raw, dict):
            appeals = [appeals_raw] if appeals_raw else []
        elif isinstance(appeals_raw, list):
            appeals = appeals_raw
        else:
            appeals = []

        filtered_appeals = []
        for a in appeals:
            if not a or not a.get("last_message_at"):
                continue
            try:
                last_msg_dt = datetime.strptime(
                    a["last_message_at"], "%d.%m.%Y %H:%M:%S"
                )
                if last_msg_dt >= from_date:
                    filtered_appeals.append(a)
            except Exception:
                continue

        stats_by_manager = {}
        for appeal in filtered_appeals:
            manager_id = appeal.get("manager_id")
            if not manager_id:
                continue
            if manager_id not in stats_by_manager:
                stats_by_manager[manager_id] = {"count": 0, "ratings": []}
            stats_by_manager[manager_id]["count"] += 1
            if appeal.get("rating") is not None:
                stats_by_manager[manager_id]["ratings"].append(appeal["rating"])

        manager_texts = []
        for manager_id, data in stats_by_manager.items():
            try:
                manager = await bot.get_chat(manager_id)
                manager_name = (
                    f"@{manager.username}"
                    if manager.username
                    else f"Оператор {manager_id}"
                )
            except Exception:
                manager_name = f"Оператор {manager_id}"
            count = data["count"]
            avg_rating = (
                round(sum(data["ratings"]) / len(data["ratings"]), 2)
                if data["ratings"]
                else "Нет оценок"
            )
            manager_texts.append(
                f"👤 <b>{manager_name}</b>:\nОбработано заявок: <b>{count}</b>\nРейтинг: <b>{avg_rating}</b>"
            )

        appeals_statuses = {}
        ratings_all = []
        for appeal in filtered_appeals:
            status_id = appeal.get("status_id")
            if status_id:
                appeals_statuses[status_id] = appeals_statuses.get(status_id, 0) + 1
            if appeal.get("rating") is not None:
                ratings_all.append(appeal["rating"])

        status_texts = []
        for status_id, count in appeals_statuses.items():
            # status_name = get_status_name(status_id) or f"Статус {status_id}"
            status_name = None
            status_texts.append(f"{status_name}: {count}")
        avg_rating = (
            round(sum(ratings_all) / len(ratings_all), 2)
            if ratings_all
            else "Нет оценок"
        )
        text = f"📊 <b>Статистика за период:</b> <i>{period} суток</i>\n\n"
        if manager_texts:
            text += "\n\n".join(manager_texts)
        else:
            text += "Нет данных по операторам\n"
        status_text = (
            "\n".join(status_texts) if status_texts else "Нет данных по статусам\n"
        )
        text += f"\n\n<b>Общая статистика:</b>\n{status_text}\n⭐ <b>Средний рейтинг:</b> {avg_rating}"

        await call.message.edit_text(text, reply_markup=admin_keyboard())
    except Exception as e:
        logger.error(f"Ошибка формирования статистики: {e} - {call.from_user.id}")
        await call.message.edit_text(
            "Произошла ошибка, попробуйте ещё раз", reply_markup=admin_keyboard()
        )


@router.message(F.text.in_(["❌ Закрыть заявку", "❌ Пӯшидани ариза"]))
async def close_appeal_by_manager(message: Message):
    try:
        appeal = None
        # appeal = get_appeal(manager_id=message.from_user.id, status_id=2)
        if not appeal:
            await message.answer("Заявка не найдена")
            return
        await del_close_timer(appeal["id"])
        update_appeal(appeal["id"], status_id=3)
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
        logger.error(f"Ошибка закрытия заявки: {e} - {message.from_user.id}")
        await message.answer("Произошла ошибка при закрытии заявки")


# @router.message(F.text)
# async def manager_answer_appeal(message: Message):
#     """Сообщения от операторов"""
#     try:
#         logger.info(f"Ответ обращению - {message.chat.id}")
#         appeal = None
#         # appeal = get_appeal(manager_id=message.chat.id, status_id=2)
#         if appeal and isinstance(appeal, dict):
#             await bot.send_message(appeal["user_id"], message.text)
#             update_appeal(
#                 appeal["id"],
#                 last_message_at=datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
#             )
#
#             await start_timer(appeal["id"], appeal["user_id"], message.from_user.id)
#         else:
#             await message.answer("Я не смог найти обращение, попробуйте позже")
#     except Exception as e:
#         logger.error(f"Ошибка ответа на обращение: {e} - {message.chat.id}")
#         await message.answer("Произошла ошибка, попробуйте ещё раз")


# @router.message(F.text)
# async def client_answer_appeal(message: Message):
#     """Сообщения от пользователя"""
#     try:
#         logger.info(f"Ответ обращению - {message.chat.id}")
#         appeal = None
#         # appeal = get_appeal(user_id=message.chat.id, status_id=2)
#         if appeal and isinstance(appeal, dict):
#             if appeal["manager_id"]:
#                 await start_timer(
#                     appeal["id"], message.from_user.id, appeal["manager_id"]
#                 )
#                 await bot.send_message(appeal["manager_id"], message.text)
#                 update_appeal(appeal["id"], last_message_at=datetime.now())
#             else:
#                 await message.answer("Дождитесь оператора")
#     except Exception as e:
#         logger.error(f"Ошибка ответа на обращение: {e} - {message.chat.id}")
#         await message.answer("Произошла ошибка, попробуйте ещё раз")


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
    router.callback_query.register(ask_period, F.data == "statistic", AdminFilter())
    router.callback_query.register(statistics, F.data.startswith("statistic-"))
    router.callback_query.register(close_appeal_by_manager, F.data == "close_appeal_by_manager")  # Если есть такая кнопка
    router.callback_query.register(set_rating, F.data.startswith("set_rating-"))

    # --- Message handlers (текстовые сообщения) ---
    # router.message.register(manager_answer_appeal, F.text)
    # router.message.register(client_answer_appeal, F.text)
    router.message.register(close_appeal_by_manager, F.text.in_(["❌ Закрыть заявку", "❌ Пӯшидани ариза"]))

    # --- Command handlers ---
    router.message.register(admin, Command(commands=["admin"]), AdminFilter())
