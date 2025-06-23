# -*- coding: utf-8 -*-
import asyncio
import logging

from loguru import logger

from database import DataBase
from dispatcher import dp
from other import bot


async def on_startup():
    try:
        await DataBase(filename="database.db").create_tables()
        bot_data = await bot.get_me()
        logger.info(f'Бот @{bot_data.username} - {bot_data.full_name} запущен')
    except Exception as e:
        logger.exception(f'Ошибка запуска: {e}')
        raise


async def on_shutdown():
    try:
        logger.info('Бот остановлен')
    except Exception as e:
        logger.exception(f'Ошибка при остановке: {e}')


async def main():
    try:
        logging.getLogger("aiogram.event").setLevel(logging.DEBUG)
        dp.shutdown.register(on_shutdown)
        dp.startup.register(on_startup)

        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f'Ошибка при запуске бота: {e}')


if __name__ == "__main__":
    asyncio.run(main())
