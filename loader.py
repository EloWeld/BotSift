

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from config import BOT_TOKEN, MONGODB_CONNECTION_URI
from middlewares.auth_middleware import AuthMiddleware
from middlewares.user_middleware import TgUserMiddleware

# Инициализация Aiogram бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
ms = MemoryStorage()
dp = Dispatcher(bot, storage=ms)
dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(TgUserMiddleware())
dp.middleware.setup(AuthMiddleware())


threads = []
pyrogram_clients = []