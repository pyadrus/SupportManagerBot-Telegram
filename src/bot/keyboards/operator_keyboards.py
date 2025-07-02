# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo


def operator_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для оператора"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Web панель",
                                  web_app=WebAppInfo(url="https://support-operator-bot.ru.tuna.am"))],
        ]
    )
