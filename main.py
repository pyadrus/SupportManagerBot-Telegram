# -*- coding: utf-8 -*-
import os
import subprocess
import sys
from loguru import logger

logger.add("log/log.log")

# Путь к корню проекта (где находится scr/)
project_root = os.path.dirname(os.path.abspath(__file__))

# Команды с указанием PYTHONPATH
commands = [
    [sys.executable, "app/app.py"],  # запускает приложение
    [sys.executable, "bot.py"],  # запускает бота
]

# Установить PYTHONPATH на корень проекта
env = os.environ.copy()
env["PYTHONPATH"] = project_root

processes = [subprocess.Popen(cmd, env=env) for cmd in commands]
