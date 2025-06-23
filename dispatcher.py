# -*- coding: utf-8 -*-
from aiogram import Dispatcher
from aiogram import Router

dp = Dispatcher()

router = Router()
dp.include_router(router)