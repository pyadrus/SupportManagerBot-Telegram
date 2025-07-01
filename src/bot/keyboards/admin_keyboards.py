# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo


def admin_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для админки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика", callback_data="statistic")],
            [InlineKeyboardButton(text="Выдать права менеджеру", callback_data="give_operator")],
            [InlineKeyboardButton(text="Web панель",
                                  web_app=WebAppInfo(url="https://support-operator-bot.ru.tuna.am"))],
        ]
    )
