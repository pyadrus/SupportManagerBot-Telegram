# app.py

from fastapi import FastAPI
from pathlib import Path
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

# === Импорт роутера авторизации ===
from auth import router as auth_router  # <-- Новый импорт

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# === Подключаем шаблоны и статику ===
app.mount("/app/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# === Регистрируем маршруты авторизации ===
app.include_router(auth_router)  # <-- Добавляем роуты из auth.py


# === Маршруты основного приложения ===
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/admin")
async def admin(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/operator")
async def operator(request: Request):
    return templates.TemplateResponse("operator.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8080, reload=True)
