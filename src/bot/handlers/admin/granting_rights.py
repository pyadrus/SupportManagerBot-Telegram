import secrets

from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.bot.states.states import GrantingStates
from src.bot.system.dispatcher import router, bot
from src.core.database.database import set_user_role


def generate_six_digit_password() -> str:
    """Безопасная генерация 6-значного пароля"""
    return f"{secrets.randbelow(900000 + 100000):06d}"


"""Выдача прав оператору"""


@router.callback_query(F.data == 'give_operator')
async def give_operator(callback_query: CallbackQuery, state: FSMContext):
    """Запрашивает ID пользователя для выдачи прав оператора"""
    await bot.send_message(
        callback_query.from_user.id,
        text="Напишите ID пользователя Telegram, которому хотите выдать права оператора:"
    )
    await state.set_state(GrantingStates.user_id)


@router.message(StateFilter(GrantingStates.user_id))
async def process_user_id(message: Message, state: FSMContext):
    """Получает ID пользователя и выдает ему роль operator с одноразовым паролем"""
    user_id = message.text.strip()
    user_id = int(user_id)
    username = "operator"
    # Генерируем пароль и устанавливаем роль
    password = generate_six_digit_password()
    stored_data = {
        "user_id": user_id,
        "username": username,
        "password": password
    }
    set_user_role(stored_data)  # Сохраняем данные в БД src/core/database/database.db
    # Отправляем результат админу
    await message.answer(
        f"✅ Пользователю с ID <b>{user_id}</b> выданы права оператора.\n"
        f"🔑 Логин доступа: <code>{username}</code>\n"
        f"🔑 Пароль доступа: <code>{password}</code>\n"
    )
    await state.clear()


def register_granting_rights_handlers():
    """Регистрирует обработчики для выдачи прав оператору"""
    router.callback_query.register(give_operator, F.data == 'give_operator')
    router.message.register(process_user_id, StateFilter(GrantingStates.user_id))
