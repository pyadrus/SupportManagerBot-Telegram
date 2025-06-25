# app.py
from fastapi import FastAPI, Request  # ← Добавлен Request
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Импортируем роутер
from auth import router as auth_router

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Подключаем статику
app.mount("/app/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Регистрируем маршруты авторизации
app.include_router(auth_router)


# === Страница оператора ===
@app.get("/operator", response_class=HTMLResponse)
async def operator_page(request: Request):
    return templates.TemplateResponse("operator.html", {"request": request})
