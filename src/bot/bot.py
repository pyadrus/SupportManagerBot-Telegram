# -*- coding: utf-8 -*-
import asyncio
import logging

from loguru import logger

from src.bot.handlers.admin.admin import register_handlers_admin
from src.bot.handlers.manager.group import register_manager_handlers_group
from src.bot.handlers.user.greet import register_commands
from src.bot.handlers.user.user import register_user_handler
from src.bot.system.dispatcher import dp, bot
from src.core.database.database import db, Person

logger.add("log/log.log")


async def on_startup():
    try:
        bot_data = await bot.get_me()
        db.create_tables([Person])  # Создание таблицы в базе данных
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
