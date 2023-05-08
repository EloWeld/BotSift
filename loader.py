

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode

from config import BOT_TOKEN

# Инициализация Aiogram бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
ms = MemoryStorage()
dp = Dispatcher(bot, storage=ms)
dp.middleware.setup(LoggingMiddleware())

pyrogram_clients = []
