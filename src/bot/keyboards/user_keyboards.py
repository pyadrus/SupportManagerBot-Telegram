# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def choose_lang() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇹🇯 Забони тоҷикӣ", callback_data="lang-tj"),
                InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data="lang-ru"),
            ]
        ]
    )


def start(lang: str) -> InlineKeyboardMarkup:
    if lang == "tj":
        btns = [
            [
                InlineKeyboardButton(
                    text="🆘 Кӯмаки мутахассис", callback_data="call_manager"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔗 Портали хизматрасониҳо", url="https://khizmat.ehukumat.tj"
                ),
                InlineKeyboardButton(
                    text="✍️ Боргирии ИМЗО",
                    url="https://play.google.com/store/apps/details?id=tj.dc.myid1a",
                ),
            ],
        ]
    elif lang == "ru":
        btns = [
            [
                InlineKeyboardButton(
                    text="🆘 Помощь специалиста", callback_data="call_manager"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔗 Портал госуслуг", url="https://khizmat.ehukumat.tj"
                ),
                InlineKeyboardButton(
                    text="✍️ Скачать ИМЗО",
                    url="https://play.google.com/store/apps/details?id=tj.dc.myid1a",
                ),
            ],
        ]
    return InlineKeyboardMarkup(inline_keyboard=btns)


def stat_period() -> InlineKeyboardMarkup:
    periods = {
        "1": "День",
        "7": "Неделя",
        "30": "Месяц",
        "90": "Квартал",
        "183": "Полгода",
        "365": "Год",
    }
    btns = []
    row = []
    for key, value in periods.items():
        row.append(InlineKeyboardButton(text=value, callback_data=f"statistic-{key}"))
        if len(row) == 2:
            btns.append(row)
            row = []
    return InlineKeyboardMarkup(inline_keyboard=btns)


def close_appeal(lang) -> ReplyKeyboardMarkup:
    btns = [
        [
            KeyboardButton(
                text="❌ Пӯшидани ариза" if lang == "tj" else "❌ Закрыть заявку"
            )
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=btns, resize_keyboard=True, one_time_keyboard=True
    )


def set_rating(appeal_id: int) -> InlineKeyboardMarkup:
    btns = []
    row = []
    for i in range(5):
        row.append(
            InlineKeyboardButton(
                text=str(i + 1), callback_data=f"set_rating-{appeal_id}-{i + 1}"
            )
        )
        if len(row) == 3 or i == 4:
            btns.append(row)
            row = []
    return InlineKeyboardMarkup(inline_keyboard=btns)


def manage_appeal() -> InlineKeyboardMarkup:
    btns = [
        [InlineKeyboardButton(text="✅ Взять в работу", callback_data="accept_appeal")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=btns)


def consent_or_edit_my_appeal(lang) -> InlineKeyboardMarkup:
    btns = [
        [
            InlineKeyboardButton(
                text="✅ Ҳама чиз хуб аст" if lang == "tj" else "✅ Всё в порядке",
                callback_data="consent_my_appeal",
            )
        ],
        [
            InlineKeyboardButton(
                text="✏️️ Таҳрир" if lang == "tj" else "✏️ Редактировать",
                callback_data="edit_my_appeal",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=btns)


def edit_my_appeal(lang) -> InlineKeyboardMarkup:
    btns = [
        [
            InlineKeyboardButton(
                text="✍️ Тағйир додани Номи пурра" if lang == "tj" else "✍️ Изменить ФИО",
                callback_data="edit_appeal-fio",
            )
        ],
        [
            InlineKeyboardButton(
                text=(
                    "📞 Тағйир додани телефон"
                    if lang == "tj"
                    else "📞 Изменить телефон"
                ),
                callback_data="edit_appeal-phone",
            )
        ],
        [
            InlineKeyboardButton(
                text="❓ Тағйир додани савол" if lang == "tj" else "❓ Изменить вопрос",
                callback_data="edit_appeal-question",
            )
        ],
        [
            InlineKeyboardButton(
                text="✅ Ирсол" if lang == "tj" else "✅ Отправить",
                callback_data="consent_my_appeal",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=btns)
