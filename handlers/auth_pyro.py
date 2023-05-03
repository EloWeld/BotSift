import asyncio
from aiogram import Bot, Dispatcher, types
from loader import *
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import *
from config import API_ID, API_HASH, BOT_TOKEN, MDB
from models import TgUser
from states import AuthSessionState
import pyrogram
from pyrogram.errors import FloodWait, SessionPasswordNeeded

@dp.message_handler(Command("auth_session"))
async def add_session_handler(message: types.Message):
    """
    Обработчик команды /add_session. Запрашивает имя сессии у пользователя.
    """
    await message.reply("Введите имя сессии:")
    await AuthSessionState.session_name.set()

@dp.message_handler(state=AuthSessionState.session_name)
async def session_name_handler(message: types.Message, state: FSMContext):
    """
    Обработчик ввода имени сессии. Создает новый экземпляр Pyrogram клиента и авторизует его.
    """
    session_name = message.text
    await state.update_data(session_name=session_name)
    await message.reply("Введите ваш логин(Номер телефона):")
    await AuthSessionState.login.set()
    

async def login_handler(message: types.Message, state: FSMContext):
    """
    Обработчик ввода логина. Создает новый экземпляр Pyrogram клиента и отправляет код подтверждения.
    """
    global pyrogram_clients
    login = message.text
    await state.update_data(login=login)

    # Создаем новый экземпляр Pyrogram клиента
    client = pyrogram.Client(":memory:", api_id=API_ID, api_hash=API_HASH)
    pyrogram_clients.append(client)

    try:
        await client.connect()
        await client.send_code(login)
    except FloodWait as e:
        await message.reply(f"Подождите {e.x} секунд.")
        return

    await message.reply("Код подтверждения был отправлен на ваш аккаунт. Введите его:")
    await AuthSessionState.code.set()

@dp.message_handler(state=AuthSessionState.code)
async def code_handler(message: types.Message, state: FSMContext):
    """
    Обработчик ввода кода подтверждения. Авторизует клиента Pyrogram.
    """
    global pyrogram_clients
    code = message.text
    data = await state.get_data()
    login = data["login"]

    client: pyrogram.Client = pyrogram_clients[-1]

    try:
        await client.sign_in(login, code)
    except SessionPasswordNeeded:
        await message.reply("Для этого аккаунта требуется двухфакторная аутентификация. Введите ваш пароль:")
        await AuthSessionState.password.set()
    except Exception as e:
        await message.reply(f"Ошибка: {e}")
    else:
        MDB.PyroSessions.insert_one(dict(user_id=user.user_id,
                                        session_name=data['session_name'],
                                        password=None))
        await message.reply("Сессия успешно авторизована.")
        await state.finish()

@dp.message_handler(state=AuthSessionState.password)
async def password_handler(message: types.Message, state: FSMContext):
    """
    Обработчик ввода пароля для двухфакторной аутентификации. Авторизует клиента Pyrogram.
    """
    global pyrogram_clients
    password = message.text
    client: pyrogram.Client = pyrogram_clients[-1]
    data = await state.get_data()

    try:
        await client.check_password(password)
    except Exception as e:
        await message.reply(f"Ошибка: {e}")
    else:
        MDB.PyroSessions.insert_one(dict(user_id=user.user_id,
                                        session_name=data['session_name'],
                                        password=password))
        await message.reply("Сессия успешно авторизована.")
        await state.finish()