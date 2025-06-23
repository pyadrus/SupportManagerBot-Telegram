import asyncio
import logging
from pathlib import Path
from sys import path

path.append(str(Path(__file__).parent))

from database import db
from aiogram import Dispatcher
from other import get_logger, bot
from handlers.commands import router as cmd_rt
from handlers.user import router as user_rt
from handlers.admin import router as adm_rt
from handlers.group import router as group_rt

dp = Dispatcher()
dp.include_routers(cmd_rt, user_rt, adm_rt, group_rt)

logger = get_logger(__name__)


async def on_startup():
    try:
        await db.create_tables()
        bot_data = await bot.get_me()
        logger.info(f'Бот @{bot_data.username} - {bot_data.full_name} запущен')
    except Exception as e:
        logger.critical(f'Ошибка запуска: {e}')
        raise

async def on_shutdown():
    try:
        logger.info('Бот остановлен')
    except Exception as e:
        logger.error(f'Ошибка при остановке: {e}')

async def main():
    try:
        logging.getLogger("aiogram.event").setLevel(logging.DEBUG)
        dp.shutdown.register(on_shutdown)
        dp.startup.register(on_startup)
        
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f'Ошибка при запуске бота: {e}')

if __name__ == "__main__":
    asyncio.run(main())