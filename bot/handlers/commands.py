from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from bot.markups import choose_lang, admin_keyboard

from bot.middlewares import AdminFilter
from bot.other import get_logger

logger = get_logger(__name__)
router = Router()

@router.message(CommandStart())
async def start(message: Message):
    try:
        logger.info(f'Введена команда /start - {message.chat.id}')
        await message.answer("👋 <b>Добро пожаловать! Выберите язык общения</b> / <b>Хуш омадед! Забони муомиларо интихоб кунед:</b>", reply_markup=choose_lang())
    except Exception as e:
        logger.error(f"Ошибка /start: {e} - {message.chat.id}")
    
@router.message(Command(commands=['admin']), AdminFilter())
async def admin(message: Message):
    try:
        logger.info(f'Введена команда /admin - {message.chat.id}')
        await message.answer(f"Здравствуйте, {message.from_user.first_name}! Вы попали в админ панель", reply_markup=admin_keyboard())
    except Exception as e:
        logger.error(f"Ошибка /admin: {e} - {message.chat.id}")
    