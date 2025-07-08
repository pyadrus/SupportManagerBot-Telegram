from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi import Form
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from pydantic import BaseModel

# тут ты можешь искать в базе данных, например:
from src.core.database.database import Person  # адаптируй под свою структуру
from src.core.database.database import get_all_authorization_data, get_appeal

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Подключаем статику (стили, скрипты)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# Путь к шаблонам
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# === Страница оператора ===

@app.get("/operator", response_class=HTMLResponse)
async def operator_page(request: Request):
    return templates.TemplateResponse("operator.html", {
        "request": request,
    })


# Модель запроса
class UserID(BaseModel):
    user_id: int


@app.post("/api/set_user_id")
async def set_user_id(data: UserID):
    user_id = data.user_id
    logger.debug(f"Пользователь зашел с ID: {user_id}")
    appeal = get_appeal(operator_id=user_id)
    logger.debug(appeal)

    user = Person.get_or_none(Person.id_user == user_id)
    if user:
        return {"status": "ok", "message": "Пользователь найден", "username": user.username}
    else:
        return {"status": "not_found", "message": "Пользователь не найден"}


# === Страница администратора ===
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


# === Убираем /login, делаем всё на главной ===


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """
    Отображает форму авторизации на главной странице.
    """
    # Получаем данные авторизации из базы данных src/core/database/database.db

    return templates.TemplateResponse(
        "index.html", {"request": request, "error": error}
    )


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
