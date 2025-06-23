# -*- coding: utf-8 -*-
from aiogram import Dispatcher, Bot
from aiogram import Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings

dp = Dispatcher()

router = Router()
dp.include_router(router)

bot = Bot(token=settings.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
