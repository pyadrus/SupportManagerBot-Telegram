# -*- coding: utf-8 -*-
from aiogram.fsm.state import StatesGroup, State


class StartAppealStates(StatesGroup):
    fio = State()
    phone = State()
    question = State()
    edit_type = State()  # fio, phone, question
    edit = State()  # Измененная информация


class GrantingStates(StatesGroup):
    user_id_operator = State()  # id пользователя (оператора)
    user_id_admin = State()  # id пользователя (администратора)
