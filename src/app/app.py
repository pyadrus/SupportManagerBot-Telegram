from pathlib import Path
from typing import Dict, List
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi import Form
from fastapi import WebSocket
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from src.core.database.database import get_all_authorization_data

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Подключаем статику (стили, скрипты)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# Путь к шаблонам
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# === Страница оператора ===
# ====== ПОДКЛЮЧЕНИЯ ======
# active_connections: Dict[int, List[WebSocket]] = {}


@app.get("/operator", response_class=HTMLResponse)
async def operator_page(request: Request):
    return templates.TemplateResponse("operator.html", {
        "request": request,
        # "operator_id": operator_id
    })


# @app.websocket("/ws/{appeal_id}")
# async def websocket_endpoint(websocket: WebSocket, appeal_id: int):
#     await websocket.accept()
#     if appeal_id not in active_connections:
#         active_connections[appeal_id] = []
#     active_connections[appeal_id].append(websocket)
#     logger.info(f"Новое подключение к appeal_id={appeal_id}")
#
#     try:
#         while True:
#             data = await websocket.receive_json()
#
#             message_text = data.get("message_text")
#             sender = data.get("sender", "operator")
#             operator_id = data.get("operator_id", None)
#             user_id = data.get("user_id", None)
#
#             logger.info(f"[{sender}] {message_text}")
#
#             # Отправляем всем подключённым к этому appeal
#             for conn in active_connections[appeal_id]:
#                 await conn.send_json({
#                     "message_text": message_text,
#                     "sender": sender,
#                     "timestamp": datetime.now().strftime("%H:%M")
#                 })
#
#             # === Обновление БД и Telegram ===
#             if sender == "operator" and operator_id:
#                 try:
#                     # Получаем обращение
#                     appeal = get_appeal(user_id=user_id)
#                     if not appeal:
#                         raise Exception("Обращение не найдено")
#
#                     # Отправляем сообщение в Telegram
#                     await bot.send_message(
#                         user_id,
#                         f"🧑‍💻 Оператор:\n{message_text}"
#                     )
#
#                     # Обновляем данные обращения
#                     update_appeal(
#                         appeal_id=appeal_id,
#                         status="В обработке",
#                         operator_id=operator_id,
#                         last_message_at=datetime.now()
#                     )
#
#                     # Сохраняем сообщение
#                     write_to_db(
#                         appeal_id=appeal_id,
#                         operator_id=operator_id,
#                         user_id=None,
#                         message_text=message_text,
#                         name_db=operator_id
#                     )
#
#                     # Перезапуск таймера
#                     await start_timer(appeal_id, user_id, operator_id)
#                     logger.info(f"Таймер запущен: appeal_id={appeal_id}")
#                 except Exception as e:
#                     logger.exception(f"Ошибка при отправке сообщения от оператора: {e}")
#             else:
#                 logger.info("Пропущено сохранение: не оператор или нет operator_id")
#
#     except WebSocketDisconnect:
#         active_connections[appeal_id].remove(websocket)
#         logger.info(f"Отключение от appeal_id={appeal_id}")
#         if not active_connections[appeal_id]:
#             del active_connections[appeal_id]


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
