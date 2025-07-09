# -*- coding: utf-8 -*-
import os
from groq import Groq
from loguru import logger

user_dialogs = {}  # Словарь для хранения истории диалогов

# Получение переменных окружения
GROQ_KEY = os.getenv('GROQ_KEY')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
PORT = os.getenv('PORT')
IP = os.getenv('IP')


def setup_proxy():
    """Устанавливает прокси из переменных окружения, если они заданы"""
    if USER and PASSWORD and IP and PORT:
        proxy = f"http://{USER}:{PASSWORD}@{IP}:{PORT}"
        os.environ['http_proxy'] = proxy
        os.environ['https_proxy'] = proxy
        logger.info("Прокси успешно установлен.")
    else:
        logger.warning("Не все переменные прокси заданы. Прокси не будет использован.")


async def get_chat_completion(error: str, knowledge_base_content: str = "") -> str:
    """Отправляет текст ошибки в Groq и возвращает объяснение на русском языке"""
    try:
        # Установка прокси
        setup_proxy()

        # Проверка наличия API-ключа
        if not GROQ_KEY:
            logger.error("GROQ_KEY не задан в переменных окружения.")
            return "Ошибка: отсутствует ключ API для Groq."

        # Инициализация клиента
        client = Groq(api_key=GROQ_KEY)

        # Модель и промт
        model_name = "meta-llama/llama-4-scout-17b-16e-instruct"
        system_prompt = (
            "Ты — опытный Python-разработчик. Объясни, что означает эта ошибка на ПОНЯТНОМ русском языке, "
            "и как её можно исправить. Укажи возможные причины."
        )

        logger.info(f"Используемая модель: {model_name}")
        logger.debug(f"Системный промт: {system_prompt}")
        logger.debug(f"Текст ошибки: {error}")

        # Запрос к модели
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"{system_prompt}\n\n{knowledge_base_content}"},
                {"role": "user", "content": error},
            ],
            model=model_name,
        )

        answer = response.choices[0].message.content
        logger.debug(f"Ответ от модели: {answer}")
        return answer

    except Exception as e:
        logger.exception("Произошла ошибка при обращении к Groq API")
        return "⚠️ Не удалось получить ответ от ИИ. Проверьте подключение и корректность данных."
