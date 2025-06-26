# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для админки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Статистика", callback_data="statistic")],
            [InlineKeyboardButton(text="Выдать права менеджеру", callback_data="give_manager")]
        ]
    )
