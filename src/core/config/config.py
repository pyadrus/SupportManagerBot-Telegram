# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

# Загрузка переменных из .env файла
load_dotenv()

# Чтение переменных
TOKEN = os.getenv("TOKEN")
LOG_TYPE = os.getenv("LOG_TYPE")
ADMIN = int(os.getenv("ADMIN"))  # Преобразуем в int
DB_NAME = os.getenv("DB_NAME")
GROUP_ID = int(os.getenv("GROUP_ID"))  # Также преобразуем в int

# Вывод (для проверки)
print("TOKEN:", TOKEN)
print("LOG_TYPE:", LOG_TYPE)
print("ADMIN:", ADMIN)
print("DB_NAME:", DB_NAME)
print("GROUP_ID:", GROUP_ID)
