# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from aiogram import F
from aiogram.types import CallbackQuery
from loguru import logger

from src.bot.keyboards.admin_keyboards import admin_keyboard
from src.bot.keyboards.user_keyboards import stat_period
from src.bot.middlewares.middlewares import AdminFilter
from src.bot.system.dispatcher import bot, router


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


def register_handlers_getting_statistics():
    # --- Callback handlers ---
    router.callback_query.register(ask_period, F.data == "statistic", AdminFilter())
    router.callback_query.register(statistics, F.data.startswith("statistic-"))
