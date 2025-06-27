from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI
from fastapi import Form
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Укажи путь к шаблонам
TEMPLATES_DIR = "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Подключаем статику
# app.mount("/app/static", StaticFiles(directory=STATIC_DIR), name="static")


# === Страница оператора ===
@app.get("/operator", response_class=HTMLResponse)
async def operator_page(request: Request):
    return templates.TemplateResponse("operator.html", {"request": request})


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


# Пример данных пользователя
VALID_USERS = {
    "admin": {"password": "12345", "role": "admin"},
    "operator": {"password": "12345", "role": "operator"}
}


# === Убираем /login, делаем всё на главной ===

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None):
    """
    Отображает форму авторизации на главной странице.
    """
    return templates.TemplateResponse("index.html", {"request": request, "error": error})


@app.post("/login")
async def login(
        username: str = Form(...),
        password: str = Form(...)
):
    """
    Проверяет логин и пароль.
    Если верные — перенаправляет на /operator.
    Иначе — возвращает на главную с ошибкой.
    """
    user = VALID_USERS.get(username)
    if user and user["password"] == password:
        if user["role"] == "admin":
            return RedirectResponse(url="/admin", status_code=303)
        else:
            return RedirectResponse(url="/operator", status_code=303)

    return RedirectResponse(url="/?error=Неверный+логин+или+пароль", status_code=303)


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
