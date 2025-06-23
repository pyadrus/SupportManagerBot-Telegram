# -*- coding: utf-8 -*-
import inspect
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from os import path, makedirs

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import settings

bot = Bot(token=settings.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'WARNING': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICAL': '\033[41m'
    }
    RESET = '\033[0m'

    def format(self, record):
        frame = inspect.currentframe()
        while frame:
            frame = frame.f_back
            if frame.f_globals.get('__name__') == __name__:
                continue
            info = inspect.getframeinfo(frame)
            record.caller = f"{path.basename(info.filename)}:{info.lineno}"
            break

        color = self.COLORS.get(record.levelname, '')
        message = super().format(record)
        return f"{color}{message}{self.RESET}" if color else message


def get_logger(logger_name: str) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    if logger.hasHandlers():
        logger.handlers.clear()
    format = '%(asctime)s [%(filename)s:%(lineno)s] | %(levelname)s | %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    if settings.LOG_TYPE == 'console':
        handler = logging.StreamHandler()
        handler.setFormatter(ColoredFormatter(format, date_format))
    else:
        log_dir = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'logs')
        makedirs(log_dir, exist_ok=True)
        handler = TimedRotatingFileHandler(filename=path.join(log_dir, 'app.log'), when='W0', interval=1, backupCount=4,
                                           encoding='UTF-8', atTime=datetime.min.time())
        handler.setFormatter(ColoredFormatter(format, date_format))

    logger.addHandler(handler)
    if settings.LOG_TYPE == 'file':
        import atexit
        atexit.register(handler.close)
    return logger


logger = get_logger(__name__)
