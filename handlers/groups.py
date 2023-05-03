
import asyncio
from aiogram import Bot, Dispatcher, types
from loader import *
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import *
from config import API_ID, API_HASH, BOT_TOKEN
from models import TgUser
from states import AuthSessionState

# Команда добавления группы
@dp.message_handler(commands=["addgroup"])
async def add_group(message: types.Message):
    try:
        chat_id, list_name, *keywords = message.text.split()
    except Exception as e:
        await message.answer(f"Ошибка при обработке команды")
    minus_words = []

    if not keywords:
        await message.reply("Укажите ключевые слова после команды.")
        return

    added = await db.add_group(chat_id, list_name, keywords, minus_words)
    if added:
        await message.reply("Группа успешно добавлена.")
    else:
        await message.reply("Группа уже существует.")


# Команда удаления группы
@dp.message_handler(commands=["removegroup"])
async def remove_group(message: types.Message):
    chat_id = message.chat.id

    removed = await db.remove_group(chat_id)
    if removed:
        await message.reply("Группа успешно удалена.")
    else:
        await message.reply("Группа не найдена.")


# Команда добавления пользователя в черный список
@dp.message_handler(commands=["addban"])
async def add_ban(message: types.Message):
    user_id = int(message.text.split()[1])

    added = await db.add_to_blacklist(user_id)
    if added:
        await message.reply("Пользователь успешно добавлен в черный список.")
    else:
        await message.reply("Пользователь уже в черном списке.")


# Команда удаления пользователя из черного списка
@dp.message_handler(commands=["removeban"])
async def remove_ban(message: types.Message):
    user_id = int(message.text.split()[1])

    removed = await db.remove_from_blacklist(user_id)
    if removed:
        await message.reply("Пользователь успешно удален из черного списка.")
    else:
        await message.reply("Пользователь не найден в черном списке.")
