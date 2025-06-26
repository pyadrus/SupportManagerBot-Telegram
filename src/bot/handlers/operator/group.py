# -*- coding: utf-8 -*-
import re
from datetime import datetime
from typing import Optional

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from loguru import logger

from src.bot.keyboards.keyboards import close_appeal
from src.bot.system.dispatcher import router, bot
from src.core.database.database import db


@router.callback_query(F.data == 'accept_appeal')
async def accept_appeal(callback_query: CallbackQuery, state: FSMContext):
    try:
        manager = await db.get_user(callback_query.from_user.id)
        if await db.check_manager_active_appeal(callback_query.from_user.id):
            await callback_query.answer("У Вас есть активное обращение", show_alert=True)
        elif not manager:
            await callback_query.answer("Вы не зарегистрированы в боте", show_alert=True)
        else:
            text = callback_query.message.html_text
            appeal_id = extract_appeal_id(text)
            if appeal_id:
                appeal = await db.get_appeal(id=appeal_id)
                if appeal['user_id'] == callback_query.from_user.id:
                    await callback_query.answer("Вы не можете принять свою заявку", True)
                    return
                await callback_query.message.edit_text(
                    f"{text}\n\n🔥 Заявка принята {f'@{callback_query.from_user.username}' if callback_query.from_user.username else f'<code>{callback_query.from_user.id}</code>'}\n🕛 Дата принятия: <code>{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</code>")
                await bot.send_message(callback_query.from_user.id, f"Вы приняли заявку:\n{text}",
                                       reply_markup=close_appeal(appeal_id))
                client_lang = await db.get_user_lang(appeal['user_id'])
                await bot.send_message(appeal['user_id'],
                                       "🤝 <b>Мутахассис ба дархости шумо пайваст шуд.</b> Шумо метавонед оғоз кунед ✨" if client_lang == "tj" else "🤝 <b>Специалист подключился к вашему запросу.</b> Можете начать общение ✨")
                await db.update_appeal_data(appeal_id, status_id=2, manager_id=callback_query.from_user.id)
            else:
                await callback_query.message.edit_text("В обращении не найден id")
    except Exception as e:
        logger.error(f"Ошибка принятия заявки: {e} - {callback_query.message.chat.id}")
    finally:
        await state.clear()


def extract_appeal_id(text: str) -> Optional[int]:
    """Извлекает ID обращения из текста"""
    try:
        match = re.search(r'🆔\s*<code>#(\d+)</code>', text)
        if match:
            return int(match.group(1))
    except Exception as e:
        print(f"Ошибка при извлечении ID: {e}")


def register_manager_handlers_group():
    router.callback_query.register(accept_appeal, F.data == 'accept_appeal')
