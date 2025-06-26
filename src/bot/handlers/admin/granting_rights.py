import secrets

from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from src.bot.states.states import GrantingStates
from src.bot.system.dispatcher import router, bot
from src.core.database.database import set_user_role, UserRole


def get_user_role(user_id: int) -> str:
    """Возвращает роль пользователя"""
    try:
        role_record = UserRole.get_or_none(UserRole.user == user_id)
        return role_record.role if role_record else "user"
    except Exception as e:
        logger.error(f"Ошибка получения роли для {user_id}: {e}")
        return "user"


def check_user_password(user_id: int, entered_password: str) -> bool:
    """Проверяет, совпадает ли введённый пароль с сохранённым"""
    try:
        access = UserRole.get_or_none(UserRole.user == user_id)
        return access and access.password == entered_password
    except Exception as e:
        logger.error(f"Ошибка проверки пароля: {e}")
        return False


# === Генерация пароля ===
def generate_six_digit_password() -> str:
    """Безопасная генерация 6-значного пароля"""
    return f"{secrets.randbelow(900000 + 100000):06d}"


# === Логика выдачи роли через FSM ===

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

    if not user_id.isdigit():
        await message.answer("❌ Неверный формат ID. Пожалуйста, введите корректный числовой ID.")
        return

    user_id = int(user_id)
    username = "operator"
    try:
        # Генерируем пароль и устанавливаем роль
        password = generate_six_digit_password()
        set_user_role(user_id=user_id, role=username, password=password)

        # Отправляем результат админу
        await message.answer(
            f"✅ Пользователю с ID <b>{user_id}</b> выданы права оператора.\n"
            f"🔑 Логин доступа: <code>{username}</code>\n"
            f"🔑 Пароль доступа: <code>{password}</code>\n"
        )

        await state.clear()
    except Exception as e:
        logger.exception(f"Ошибка при выдаче прав оператору: {e}")
        await message.answer("❌ Произошла ошибка при выдаче прав.")


def register_granting_rights_handlers():
    """Регистрирует обработчики для выдачи прав оператору"""
    router.callback_query.register(give_operator, F.data == 'give_operator')
    router.message.register(process_user_id, StateFilter(GrantingStates.user_id))
