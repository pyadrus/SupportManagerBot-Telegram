from pathlib import Path
from typing import Optional
from loguru import logger
import uvicorn
from fastapi import FastAPI
from fastapi import Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from src.core.database.database import get_all_authorization_data

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Путь к шаблонам
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# === Страница оператора ===
@app.get("/operator", response_class=HTMLResponse)
async def operator_page(request: Request):
    return templates.TemplateResponse("operator.html", {"request": request})


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

    return templates.TemplateResponse("index.html", {"request": request, "error": error})


@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...)
):
    """
    Проверяет логин и пароль.
    Если верные — перенаправляет на /operator или /admin.
    Иначе — возвращает на главную с ошибкой.
    """

    data = get_all_authorization_data()
    logger.debug("✅ Данные из БД: {}", data)

    # Поиск пользователя с совпадающим username и password
    user_match = None
    for entry in data:
        if entry['username'] == username and entry['password'] == password:
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


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
