# -*- coding: utf-8 -*-
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# === Подключаем шаблоны и статику ===
app.mount("/app/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


# === Маршруты ===


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Отображение стартовой страницы с приветствием пользователя.

    :param request: Объект запроса.
    :return: HTML-страница с приветствием.

    """
    return templates.TemplateResponse("index.html", {"request": request})


# Новый маршрут админов
@app.get("/admin")
async def admin(request: Request):
    return templates.TemplateResponse(
        "admin.html", {"request": request}
    )


# Новый маршрут операторов
@app.get("/operator")
async def operator(request: Request):
    return templates.TemplateResponse(
        "operator.html", {"request": request}
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
