# -*- coding: utf-8 -*-
import os
from groq import Groq
from loguru import logger

from src.core.config.config import USER, IP, PORT, PASSWORD, GROQ_KEY


def setup_proxy():
    # Указываем прокси для HTTP и HTTPS
    os.environ['http_proxy'] = f"http://{USER}:{PASSWORD}@{IP}:{PORT}"
    os.environ['https_proxy'] = f"http://{USER}:{PASSWORD}@{IP}:{PORT}"


async def get_chat_completion(error):
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
                {"role": "system", "content": f"{system_prompt}"},
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
