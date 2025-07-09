# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import Body
from fastapi import FastAPI, Request
from fastapi import Form
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import BaseModel

# тут ты можешь искать в базе данных, например:
from src.core.database.database import get_all_authorization_data, get_appeal
from src.core.database.dialogues import get_operator_dialog
from src.core.database.operator_db import get_operator_table

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Подключаем статику (стили, скрипты)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# Путь к шаблонам
templates = Jinja2Templates(directory=TEMPLATES_DIR)

"""
Коды ошибок:
    404 - страница не найдена
    500 - ошибка сервера
    403 - запрещено
    200 - все ок
    201 - создано
    204 - пусто
    202 - в обработке
    303 - перенаправление
    401 - не авторизован
    405 - метод не поддерживается
"""


# === Страница оператора ===

@app.get("/operator", response_class=HTMLResponse)
async def operator_page(request: Request):
    """Переходим на страницу оператора"""
    return templates.TemplateResponse("operator.html", {
        "request": request,
    })


# Модель запроса
class UserID(BaseModel):
    user_id: int


@app.post("/api/set_user_id_table")
async def set_user_id_table(data: UserID = Body(...)):
    """Получаем ID пользователя и возвращаем его в формате JSON"""
    try:
        user_id = data.user_id  # Получаем ID пользователя из запроса
        logger.debug(f"Пользователь зашел с ID: {user_id}")  # Логируем ID

        tables = get_operator_table(user_id)  # Получаем таблицу из базы данных
        return JSONResponse({"tables": tables})  # Возвращаем таблицу в формате JSON
    except Exception as e:
        logger.exception(e)
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/set_user_id")
async def set_user_id(data: UserID):
    """Получает ID пользователя и возвращает диалоги из базы данных"""
    try:
        user_id = data.user_id  # Получаем ID пользователя из запроса
        logger.debug(f"Пользователь зашел с ID: {user_id}")  # Логируем ID

        appeal = get_appeal(operator_id=user_id)  # Получаем обращение по ID оператора
        dialogs = get_operator_dialog(name_db=appeal["operator_id"], appeal_id=appeal["id"])

        return JSONResponse({"dialogs": dialogs})  # Возвращаем диалоги в формате JSON

    except Exception as e:
        logger.exception(e)  # Логируем ошибку
        return JSONResponse({"error": str(e)}, status_code=500)  # Возвращаем ошибку с кодом 500


@app.get("/operator/dialogs", response_class=HTMLResponse)
async def show_operator_dialogs(request: Request):
    """Переходим на страницу с диалогами оператора"""
    try:
        return templates.TemplateResponse("operator_dialogs.html", {"request": request})
    except Exception as e:
        logger.exception(e)


# === Страница администратора ===
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    try:
        return templates.TemplateResponse("admin.html", {"request": request})
    except Exception as e:
        logger.exception(e)


# === Убираем /login, делаем всё на главной ===


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """
    Отображает форму авторизации на главной странице.
    """
    # Получаем данные авторизации из базы данных src/core/database/database.db
    try:
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": error}
        )
    except Exception as e:
        logger.exception(e)


@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Проверяет логин и пароль.
    Если верные — перенаправляет на /operator или /admin.
    Иначе — возвращает на главную с ошибкой.
    """
    try:
        data = get_all_authorization_data()
        logger.debug("✅ Данные из БД: {}", data)

        # Поиск пользователя с совпадающим username и password
        user_match = None
        for entry in data:
            if entry["username"] == username and entry["password"] == password:
                user_match = entry
                break

        if user_match:
            if username == "admin":
                return RedirectResponse(url="/admin", status_code=303)
            else:
                return RedirectResponse(url="/operator", status_code=303)

        # Если совпадений нет
        logger.warning("❌ Неверный логин или пароль")
        return RedirectResponse(url="/?error=Неверный+логин+или+пароль", status_code=303)
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
