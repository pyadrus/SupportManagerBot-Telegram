# -*- coding: utf-8 -*-
from aiogram import Dispatcher, Bot
from aiogram import Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.bot.bot import TOKEN

dp = Dispatcher()

router = Router()
dp.include_router(router)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
