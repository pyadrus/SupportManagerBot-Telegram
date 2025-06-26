# -*- coding: utf-8 -*-
from datetime import datetime

from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from src.bot.keyboards.keyboards import consent_or_edit_my_appeal, manage_appeal, edit_my_appeal
from src.bot.states.states import StartAppealStates
from src.bot.system.dispatcher import router, bot
from src.core.config.config import GROUP_ID
from src.core.database.database import db



@router.callback_query(F.data == 'give_operator')
async def give_operator(callback_query: CallbackQuery, state: FSMContext):
    """Выдает права оператору"""
    await bot.send_message(callback_query.from_user.id, text="Напишите ID пользователя Telegram, для выдачи ему права оператора")


def register_granting_rights_handlers():
    """Регистрирует обработчиков для выдачи прав оператору"""
    router.callback_query.register(give_operator, F.data == 'give_operator')
