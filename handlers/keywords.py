import asyncio
from aiogram import Bot, Dispatcher, types
from loader import *
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import *
from config import API_ID, API_HASH, BOT_TOKEN
from database import db
from models import TgUser
from states import AuthSessionState

# Команда добавления ключевых слов
@dp.message_handler(commands=["addkeywords"])
async def add_keywords(message: types.Message):
    chat_id, list_name, *new_keywords = message.text.split()

    if not new_keywords:
        await message.reply("Укажите ключевые слова после команды.")
        return

    updated = await db.add_keywords(chat_id, list_name, new_keywords)
    if updated:
        await message.reply("Ключевые слова успешно добавлены.")
    else:
        await message.reply("Группа не найдена.")


# Команда удаления ключевых слов
@dp.message_handler(commands=["removekeywords"])
async def remove_keywords(message: types.Message):
    chat_id = message.chat.id
    keywords_to_remove = message.text.split()[1:]

    if not keywords_to_remove:
        await message.reply("Укажите ключевые слова после команды.")
        return

    updated = await db.remove_keywords(chat_id, keywords_to_remove)
    if updated:
        await message.reply("Ключевые слова успешно удалены.")
    else:
        await message.reply("Группа не найдена или ключевые слова не найдены.")

