from datetime import datetime

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.src.config import settings
from bot.src.database import db
from bot.src.markups import start, consent_or_edit_my_appeal, manage_appeal, edit_my_appeal
from bot.src.other import get_logger, bot
from bot.src.states import StartAppealStates

logger = get_logger(__name__)
router = Router()


@router.callback_query(F.data.startswith("lang-"))
async def choose_lang(call: CallbackQuery, state: FSMContext):
    try:
        lang = call.data.split('-')[1]
        logger.info(f'Выбран язык {lang} - {call.from_user.id}')
        await db.add_user(call.from_user.id, lang)
        await call.message.edit_text(
            "Чӣ тавр ман метавонам кӯмак кунам, сайёҳ? ✨" if lang == 'tj' else "Чем могу помочь, путник? ✨",
            reply_markup=start(lang))
    except Exception as e:
        logger.error(f"Ошибка выбора языка: {e} - {call.from_user.id}")
    finally:
        await state.clear()


@router.callback_query(F.data == 'call_manager')
async def start_create_appeal(call: CallbackQuery, state: FSMContext):
    try:
        lang = await db.get_user_lang(call.from_user.id)
        await call.answer()
        if await db.check_user_active_appeal(call.from_user.id):
            await call.message.answer(
                "💬 Шумо аллакай дар муколамаи фаъол ҳастед" if lang == 'tj' else "💬 Вы уже находитесь в активном диалоге")
        else:
            await call.message.answer(
                "📝 Пеш аз пайваст шудан бо мутахассис, лутфан номи пурраи худро ворид кунед" if lang == 'tj' else "📝 Прежде чем связаться со специалистом, введите ваше ФИО")
            await state.set_state(StartAppealStates.fio)
    except Exception as e:
        logger.error(f"Ошибка начала создания обращения: {e} - {call.from_user.id}")


@router.message(StateFilter(StartAppealStates.fio))
async def fio_appeal(message: Message, state: FSMContext):
    try:
        await state.update_data(fio=message.text)
        lang = await db.get_user_lang(message.chat.id)
        await message.answer(
            "📞 Бузург! Акнун рақами телефони тамосатонро ворид кунед" if lang == 'tj' else "📞 Отлично! Теперь введите ваш контактный номер телефона")
        await state.set_state(StartAppealStates.phone)
    except Exception as e:
        logger.error(f"Ошибка ввода ФИО обращения: {e} - {message.chat.id}")


@router.message(StateFilter(StartAppealStates.phone))
async def phone_appeal(message: Message, state: FSMContext):
    try:
        await state.update_data(phone=message.text)
        lang = await db.get_user_lang(message.chat.id)
        await message.answer(
            "❓ Савол е мушкилоти худро ба қадри имкон муфассал тавсиф кунед" if lang == 'tj' else "❓ Опишите ваш вопрос или проблему как можно подробнее")
        await state.set_state(StartAppealStates.question)
    except Exception as e:
        logger.error(f"Ошибка ввода номера телефона обращения: {e} - {message.chat.id}")


@router.message(StateFilter(StartAppealStates.question))
async def question_appeal(message: Message, state: FSMContext):
    try:
        await state.update_data(question=message.text)
        data = await state.get_data()
        lang = await db.get_user_lang(message.chat.id)
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
async def consent_appeal(call: CallbackQuery, state: FSMContext):
    try:
        logger.info(f"Создано обращение {call.from_user.id}")
        lang = await db.get_user_lang(call.message.chat.id)
        await call.message.edit_text(
            "✅ <b>Дархости шумо қабул шуд!</b> Мунтазир бошед, мутахассиси мо ба зудӣ бо шумо тамос мегирад. Мо кор мекунем, дар ҳоле ки шаҳр хоб аст... 🌙" if lang == 'tj' else "✅ <b>Ваша заявка принята!</b> Ожидайте, наш специалист скоро свяжется с вами. Мы работаем, пока город спит... 🌙")
        appeal_id = await db.add_appeal(call.from_user.id)
        await db.update_appeal_data(appeal_id, last_message_at=datetime.now().strftime('%d.%m.%Y %H:%M:%S'))

        data = await state.get_data()
        text = f"""
🆕 Обращение {f'@{call.from_user.username}' if call.from_user.username else f'<code>{call.from_user.id}</code>'}
🆔 <code>#{appeal_id}</code>
🕛 Дата создания: <code>{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}</code>

<b>ФИО:</b> <code>{data['fio']}</code>
<b>Телефон:</b> <code>{data['phone']}</code>
<b>Вопрос:</b> <code>{data['question']}</code>
        """
        await bot.send_message(settings.GROUP_ID, text, reply_markup=manage_appeal())
    except Exception as e:
        logger.error(f"Ошибка регистрации обращения: {e} - {call.from_user.id}")
    finally:
        await state.clear()


@router.callback_query(F.data == 'edit_my_appeal')
async def start_edit_appeal(call: CallbackQuery, state: FSMContext):
    try:
        logger.info(f"Изменение обращения {call.from_user.id}")
        lang = await db.get_user_lang(call.message.chat.id)
        await call.message.delete_reply_markup()
        await call.message.answer(
            "✍️️ Дар муомилоти шумо чӣ тағир дода мешавад?" if lang == "tj" else "✍️ Что изменить в вашем обращении?",
            reply_markup=edit_my_appeal(lang))
        await state.set_state(StartAppealStates.edit_type)
    except Exception as e:
        logger.error(f"Ошибка начала изменения обращения: {e} - {call.from_user.id}")


@router.callback_query(StateFilter(StartAppealStates.edit_type), F.data.startswith('edit_appeal-'))
async def edit_type_appeal(call: CallbackQuery, state: FSMContext):
    try:
        edit_type = call.data.split("-")[1]
        logger.info(f"Изменение {edit_type} обращения {call.from_user.id}")
        await state.update_data(edit_type=edit_type)
        lang = await db.get_user_lang(call.message.chat.id)
        if edit_type == 'fio':
            await call.message.edit_text(
                "📛 Лутфан номи пурраи навро ворид кунед" if lang == "tj" else "📛 Пожалуйста, введите новое ФИО")
        elif edit_type == 'phone':
            await call.message.edit_text(
                "📞 Лутфан рақами нави телефонро ворид кунед" if lang == "tj" else "📞 Пожалуйста, введите новый номер телефона")
        else:
            await call.message.edit_text(
                "❓ Лутфан саволи навро нависед" if lang == "tj" else "❓ Пожалуйста, введите новый вопрос")
        await state.set_state(StartAppealStates.edit)
    except Exception as e:
        logger.error(f"Ошибка начала изменения обращения: {e} - {call.from_user.id}")


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
async def set_rating(call: CallbackQuery):
    try:
        lang = await db.get_user_lang(call.from_user.id)
        await call.message.edit_text("Ташаккур :)" if lang == 'tj' else "Благодарим :)")
        data = call.data.split('-')
        await db.update_appeal_data(data[1], rating=data[2])
        logger.info(f"Установлен рейтинг для обращения {data[1]} - {data[2]}")
    except Exception as e:
        logger.error(f"Ошибка установки рейтинга: {e} - {call.from_user.id}")
