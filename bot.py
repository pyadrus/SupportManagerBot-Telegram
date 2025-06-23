# -*- coding: utf-8 -*-
import asyncio
import logging

from loguru import logger

from database import db
from dispatcher import dp, bot
from handlers.greet import register_commands


async def on_startup():
    try:
        await db.create_tables()
        bot_data = await bot.get_me()
        logger.info(f'Бот @{bot_data.username} - {bot_data.full_name} запущен')
    except Exception as e:
        logger.exception(f'Ошибка запуска: {e}')
        raise


async def on_shutdown():
    try:
        logger.info('Бот остановлен')
        await bot.session.close()  # Закрытие сессии бота
    except Exception as e:
        logger.exception(f'Ошибка при остановке: {e}')


async def main():
    try:
        # Настройка логгирования (если нужно)
        logging.basicConfig(level=logging.INFO)

        # Регистрация обработчиков старта/завершения
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        # Регистрация команд
        register_commands()

        # Запуск бота
        await dp.start_polling(bot)

    except Exception as e:
        logger.exception(f'Ошибка при запуске бота: {e}')
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
