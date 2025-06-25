# auth.py
from typing import Optional

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()

# Пример данных пользователей (в реальности — из БД)
VALID_USER = {"username": "admin", "password": "12345"}

# Укажи правильный путь к шаблонам
TEMPLATES_DIR = "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """
    Отображает форму входа.
    :param request: Объект запроса.
    :param error: Сообщение об ошибке (если есть).
    """
    return templates.TemplateResponse("login.html", {"request": request, "error": error})


@router.post("/login")
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)
):
    """
    Проверяет логин и пароль.
    Если верные — перенаправляет на /admin.
    Иначе — показывает ошибку.
    """
    if username == VALID_USER["username"] and password == VALID_USER["password"]:
        return RedirectResponse(url="/admin", status_code=303)

    # Передаем сообщение об ошибке через параметр строки
    return RedirectResponse(url="/login?error=Неверный+логин+или+пароль", status_code=303)
