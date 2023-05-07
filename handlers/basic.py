import asyncio
from aiogram import Bot, Dispatcher, types
from loader import *
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import *
from config import API_ID, API_HASH, BOT_TOKEN
from models import TgUser
from states import AuthSessionState

# Start command


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    try:
        user = TgUser.objects.get({'_id': message.from_user.id})
    except TgUser.DoesNotExist:
        user = TgUser(message.from_user.id)

    # User exists already
    user.first_name = message.from_user.first_name
    user.last_name = message.from_user.last_name
    user.username = message.from_user.username
    user.save()

    # Send welcome
    await bot.send_message(chat_id=message.chat.id, text="Привет! Я твой бот.")

    # Set bot commands
    await bot.set_my_commands([
        BotCommand("start", "Презапуск бота"),
        BotCommand("help", "Помощь")
    ])


# Get statistics
@dp.message_handler(commands=["stats"])
async def get_stats(message: types.Message):
    chat_id = message.chat.id

    count = await db.get_stats(chat_id)
    await message.reply(f"Статистика: {count} сообщений.")

# Get help


@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    help_text = """
Команды для управления ботом:

/addgroup - Добавить группу для пересылки сообщений с заданными ключевыми и минус-словами
/removegroup - Удалить группу из списка
/addkeywords <слово1> <слово2> ... - Добавить ключевые слова для группы
/removekeywords <слово1> <слово2> ... - Удалить ключевые слова из группы
/addban <user_id> - Добавить пользователя в черный список
/removeban <user_id> - Удалить пользователя из черного списка
/stats - Получить статистику по группе
/help - Отобразить эту справочную информацию

Примеры использования:
/addkeywords машина смета куплю окно
/removekeywords машина смета
/addban 93292932
/removeban 93292932
"""

    await message.reply(help_text, parse_mode=ParseMode.MARKDOWN)

# Ping pong for check bot available


@dp.message_handler(commands=["ping"])
async def ping(message: types.Message):
    await message.reply("pong")
