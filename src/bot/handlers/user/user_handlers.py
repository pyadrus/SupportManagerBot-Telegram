# -*- coding: utf-8 -*-
from datetime import datetime

from aiogram import F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from loguru import logger

from src.bot.keyboards.user_keyboards import consent_or_edit_my_appeal, manage_appeal, edit_my_appeal
from src.bot.states.states import StartAppealStates
from src.bot.system.dispatcher import router, bot
from src.core.config.config import GROUP_ID
from src.core.database.database import db, get_user_lang, check_user_active_appeal, create_appeal, update_appeal


@router.callback_query(F.data == 'call_manager')
async def start_create_appeal(callback_query: CallbackQuery, state: FSMContext):
    """Отвечает на кнопку вызова специалиста (оператора)"""
    try:
        lang = get_user_lang(id_user=callback_query.from_user.id)  # Получаем язык пользователя
        logger.info(f"Язык пользователя {callback_query.from_user.id}: {lang}")
        await callback_query.answer()
        if check_user_active_appeal(callback_query.from_user.id):  # Проверяем, активно ли обращение с оператором
            await callback_query.message.answer(
                "💬 Шумо аллакай дар муколамаи фаъол ҳастед" if lang == 'tj' else "💬 Вы уже находитесь в активном диалоге")
        else:
            await callback_query.message.answer(
                "📝 Пеш аз пайваст шудан бо мутахассис, лутфан номи пурраи худро ворид кунед" if lang == 'tj' else "📝 Прежде чем связаться со специалистом, введите ваше ФИО")
            await state.set_state(StartAppealStates.fio)
    except Exception as e:
        logger.error(f"Ошибка начала создания обращения: {e} - {callback_query.from_user.id}")


@router.message(StateFilter(StartAppealStates.fio))
async def fio_appeal(message: Message, state: FSMContext):
    """Обрабатывает ФИО пользователя"""
    try:
        await state.update_data(fio=message.text)
        lang = get_user_lang(id_user=message.chat.id)  # Получаем язык пользователя
        logger.info(f"Язык пользователя {message.chat.id}: {lang}")
        await message.answer(
            "📞 Бузург! Акнун рақами телефони тамосатонро ворид кунед" if lang == 'tj' else "📞 Отлично! Теперь введите ваш контактный номер телефона")
        await state.set_state(StartAppealStates.phone)
    except Exception as e:
        logger.error(f"Ошибка ввода ФИО обращения: {e} - {message.chat.id}")


@router.message(StateFilter(StartAppealStates.phone))
async def phone_appeal(message: Message, state: FSMContext):
    """Обрабатывает номер телефона пользователя"""
    try:
        await state.update_data(phone=message.text)
        lang = get_user_lang(id_user=message.chat.id)  # Получаем язык пользователя
        logger.info(f"Язык пользователя {message.chat.id}: {lang}")
        await message.answer(
            "❓ Савол е мушкилоти худро ба қадри имкон муфассал тавсиф кунед" if lang == 'tj' else "❓ Опишите ваш вопрос или проблему как можно подробнее")
        await state.set_state(StartAppealStates.question)
    except Exception as e:
        logger.error(f"Ошибка ввода номера телефона обращения: {e} - {message.chat.id}")


@router.message(StateFilter(StartAppealStates.question))
async def question_appeal(message: Message, state: FSMContext):
    """Обрабатывает вопрос пользователя"""
    try:
        await state.update_data(question=message.text)
        data = await state.get_data()
        lang = get_user_lang(id_user=message.chat.id)  # Получаем язык пользователя
        logger.info(f"Язык пользователя {message.chat.id}: {lang}")
        if lang == 'tj':
            text = f"""📋 Лутфан маълумоти муроҷиати худро санҷед:\n
<b>👤 ФИО</b>: {data['fio']}
<b>📞 Телефон</b>: {data['phone']}
<b>❓ Савол</b>: {data['question']}
\nАгар ҳама чиз дуруст бошад, лутфан тасдиқ кунед ё агар тағйирот лозим бошад, хабар диҳед"""
        else:
            text = f"""📋 Пожалуйста, проверьте данные вашей заявки:\n
<b>👤 ФИО</b>: {data['fio']}
<b>📞 Телефон</b>: {data['phone']}
<b>❓ Вопрос</b>: {data['question']}
\nЕсли всё верно, подтвердите, иначе измените данные"""
        await message.answer(text, reply_markup=consent_or_edit_my_appeal(lang))
    except Exception as e:
        logger.error(f"Ошибка ввода вопроса обращения: {e} - {message.chat.id}")


@router.callback_query(F.data == 'consent_my_appeal')
async def consent_appeal(callback_query: CallbackQuery, state: FSMContext):
    try:
        logger.info(f"Создано обращение {callback_query.from_user.id}")
        lang = get_user_lang(id_user=callback_query.from_user.id)  # Получаем язык пользователя
        logger.info(f"Язык пользователя {callback_query.from_user.id}: {lang}")
        await callback_query.message.edit_text(
            "✅ <b>Дархости шумо қабул шуд!</b> Мунтазир бошед, мутахассиси мо ба зудӣ бо шумо тамос мегирад. Мо кор мекунем, дар ҳоле ки шаҳр хоб аст... 🌙" if lang == 'tj' else "✅ <b>Ваша заявка принята!</b> Ожидайте, наш специалист скоро свяжется с вами. Мы работаем, пока город спит... 🌙")
        appeal_id = create_appeal(callback_query.from_user.id)
        update_appeal(appeal_id, last_message_at=datetime.now().strftime('%d.%m.%Y %H:%M:%S'))

        data = await state.get_data()
        text = f"""
🆕 Обращение {f'@{callback_query.from_user.username}' if callback_query.from_user.username else f'<code>{callback_query.from_user.id}</code>'}
🆔 <code>#{appeal_id}</code>
🕛 Дата создания: <code>{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}</code>

<b>ФИО:</b> <code>{data['fio']}</code>
<b>Телефон:</b> <code>{data['phone']}</code>
<b>Вопрос:</b> <code>{data['question']}</code>
        """
        await bot.send_message(GROUP_ID, text, reply_markup=manage_appeal())
    except Exception as e:
        logger.error(f"Ошибка регистрации обращения: {e} - {callback_query.from_user.id}")
    finally:
        await state.clear()


@router.callback_query(F.data == 'edit_my_appeal')
async def start_edit_appeal(callback_query: CallbackQuery, state: FSMContext):
    try:
        logger.info(f"Изменение обращения {callback_query.from_user.id}")
        lang = await db.get_user_lang(callback_query.message.chat.id)
        await callback_query.message.delete_reply_markup()
        await callback_query.message.answer(
            "✍️️ Дар муомилоти шумо чӣ тағир дода мешавад?" if lang == "tj" else "✍️ Что изменить в вашем обращении?",
            reply_markup=edit_my_appeal(lang))
        await state.set_state(StartAppealStates.edit_type)
    except Exception as e:
        logger.error(f"Ошибка начала изменения обращения: {e} - {callback_query.from_user.id}")


@router.callback_query(StateFilter(StartAppealStates.edit_type), F.data.startswith('edit_appeal-'))
async def edit_type_appeal(callback_query: CallbackQuery, state: FSMContext):
    try:
        edit_type = callback_query.data.split("-")[1]
        logger.info(f"Изменение {edit_type} обращения {callback_query.from_user.id}")
        await state.update_data(edit_type=edit_type)
        lang = await db.get_user_lang(callback_query.message.chat.id)
        if edit_type == 'fio':
            await callback_query.message.edit_text(
                "📛 Лутфан номи пурраи навро ворид кунед" if lang == "tj" else "📛 Пожалуйста, введите новое ФИО")
        elif edit_type == 'phone':
            await callback_query.message.edit_text(
                "📞 Лутфан рақами нави телефонро ворид кунед" if lang == "tj" else "📞 Пожалуйста, введите новый номер телефона")
        else:
            await callback_query.message.edit_text(
                "❓ Лутфан саволи навро нависед" if lang == "tj" else "❓ Пожалуйста, введите новый вопрос")
        await state.set_state(StartAppealStates.edit)
    except Exception as e:
        logger.error(f"Ошибка начала изменения обращения: {e} - {callback_query.from_user.id}")


@router.message(StateFilter(StartAppealStates.edit))
async def edit_appeal(message: Message, state: FSMContext):
    try:
        logger.info(f"Изменение обращения {message.from_user.id}")
        data = await state.get_data()
        await state.update_data(**{data['edit_type']: message.text})
        data = await state.get_data()
        lang = await db.get_user_lang(message.chat.id)
        if lang == 'tj':
            text = f"""📋 Маълумот нав карда шуд, аризаро тафтиш кунед:\n
<b>👤 ФИО</b>: {data['fio']}
<b>📞 Телефон</b>: {data['phone']}
<b>❓ Савол</b>: {data['question']}
\nАгар ҳама чиз дуруст бошад, лутфан тасдиқ кунед ё агар тағйирот лозим бошад, хабар диҳед"""
        else:
            text = f"""📋 Данные обновлены, проверьте заявку:\n
<b>👤 ФИО</b>: {data['fio']}
<b>📞 Телефон</b>: {data['phone']}
<b>❓ Вопрос</b>: {data['question']}
\nЕсли всё верно, подтвердите, иначе измените данные"""
        await message.answer(text, reply_markup=consent_or_edit_my_appeal(lang))
    except Exception as e:
        logger.error(f"Ошибка изменения обращения: {e} - {message.from_user.id}")


@router.callback_query(F.data.startswith("set_rating-"))
async def set_rating(callback_query: CallbackQuery):
    try:
        lang = await db.get_user_lang(callback_query.from_user.id)
        await callback_query.message.edit_text("Ташаккур :)" if lang == 'tj' else "Благодарим :)")
        data = callback_query.data.split('-')
        await db.update_appeal_data(data[1], rating=data[2])
        logger.info(f"Установлен рейтинг для обращения {data[1]} - {data[2]}")
    except Exception as e:
        logger.error(f"Ошибка установки рейтинга: {e} - {callback_query.from_user.id}")


def register_user_handler():
    # --- Callback handlers ---
    router.callback_query.register(start_create_appeal, F.data == 'call_manager')
    router.callback_query.register(consent_appeal, F.data == 'consent_my_appeal')
    router.callback_query.register(start_edit_appeal, F.data == 'edit_my_appeal')
    router.callback_query.register(edit_type_appeal, F.data.startswith('edit_appeal-'))
    router.callback_query.register(set_rating, F.data.startswith('set_rating-'))

    # --- FSM message handlers ---
    router.message.register(fio_appeal, StateFilter(StartAppealStates.fio))
    router.message.register(phone_appeal, StateFilter(StartAppealStates.phone))
    router.message.register(question_appeal, StateFilter(StartAppealStates.question))
    router.message.register(edit_appeal, StateFilter(StartAppealStates.edit))
