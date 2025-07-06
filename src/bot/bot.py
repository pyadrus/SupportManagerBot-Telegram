# -*- coding: utf-8 -*-
import asyncio
import logging

from loguru import logger

from bot.handlers.admin.gettingя_statistics import register_handlers_getting_statistics
from src.bot.handlers.admin.admin_handlers import register_handlers_admin
from src.bot.handlers.admin.granting_rights import register_granting_rights_handlers
from src.bot.handlers.greet_handlers import register_commands
from src.bot.handlers.operator.group_handlers import register_manager_handlers_group
from src.bot.handlers.user.user_handlers import register_user_handler
from src.bot.system.dispatcher import bot, dp
from src.core.database.database import Appeal, db

logger.add("log/log.log")


async def on_startup():
    try:
        bot_data = await bot.get_me()

        with db:  # Создание таблиц в базе данных
            # Настраиваем параметры SQLite для производительности
            db.create_tables([Appeal])
            # Добавляем стандартные статусы
            logger.info("Таблицы успешно созданы или уже существуют, статусы добавлены")

        logger.info(f"Бот @{bot_data.username} - {bot_data.full_name} запущен")
    except Exception as e:
        logger.exception(f"Ошибка запуска: {e}")
        raise


async def on_shutdown():
    try:
        logger.info("Бот остановлен")
        await bot.session.close()  # Закрытие сессии бота
    except Exception as e:
        logger.exception(f"Ошибка при остановке: {e}")


async def main():
    try:
        # Настройка логгирования (если нужно)
        logging.basicConfig(level=logging.INFO)

        # Регистрация обработчиков старта/завершения
        dp.startup.register(on_startup)
        dp.shutdown.register(on_shutdown)

        # Регистрация команд
        register_commands()  # Выбор пользователем языка и приветственное сообщение бота
        register_user_handler()  # Регистрация обработчиков для пользователя
        register_handlers_admin()  # Регистрация обработчиков для админа
        register_manager_handlers_group()  # Регистрация обработчиков для менеджера
        register_granting_rights_handlers()  # Регистрация обработчиков для выдачи прав
        register_handlers_getting_statistics()  # Регистрация обработчиков для получения статистики

        # Запуск бота
        await dp.start_polling(bot)

    except Exception as e:
        logger.exception(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
