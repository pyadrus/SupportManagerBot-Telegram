# auth.py

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

router = APIRouter()

# Пример данных пользователя
VALID_USER = {"username": "admin", "password": "12345"}

# Укажи путь к шаблонам
TEMPLATES_DIR = "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# === Убираем /login, делаем всё на главной ===

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """
    Отображает форму авторизации на главной странице.
    """
    return templates.TemplateResponse("index.html", {"request": request, "error": error})


@router.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
):
    """
    Проверяет логин и пароль.
    Если верные — перенаправляет на /operator.
    Иначе — возвращает на главную с ошибкой.
    """
    if username == VALID_USER["username"] and password == VALID_USER["password"]:
        return RedirectResponse(url="/operator", status_code=303)

    return RedirectResponse(url="/?error=Неверный+логин+или+пароль", status_code=303)
