# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

# Чтение переменных
TOKEN = os.getenv("TOKEN")
ADMIN = int(os.getenv("ADMIN"))  # Преобразуем в int
DB_NAME = os.getenv("DB_NAME")

# Вывод (для проверки)
print("TOKEN:", TOKEN)
print("ADMIN:", ADMIN)
print("DB_NAME:", DB_NAME)


# Получение переменных окружения
GROQ_KEY = os.getenv('GROQ_KEY')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')
PORT = os.getenv('PORT')
IP = os.getenv('IP')