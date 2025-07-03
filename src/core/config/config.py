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
