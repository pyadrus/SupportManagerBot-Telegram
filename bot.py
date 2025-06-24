# -*- coding: utf-8 -*-
import asyncio
import logging

from loguru import logger

from database.database import db
from dispatcher import dp, bot
from handlers.admin import register_handlers_admin
from handlers.greet import register_commands
from handlers.group import register_manager_handlers_group
from handlers.user import register_user_handler


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
        register_commands()  # Выбор пользователем языка и приветственное сообщение бота
        register_user_handler()
        register_handlers_admin()  # Регистрация обработчиков для админа
        register_manager_handlers_group()

        # Запуск бота
        await dp.start_polling(bot)

    except Exception as e:
        logger.exception(f'Ошибка при запуске бота: {e}')
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
