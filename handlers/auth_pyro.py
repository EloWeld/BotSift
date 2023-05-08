import asyncio
from aiogram import Bot, Dispatcher, types
from etc.keyboards import Keyboards
from loader import *
from aiogram.dispatcher.filters import Command, ChatTypeFilter
from aiogram.dispatcher import FSMContext
from aiogram.types import *
from config import API_ID, API_HASH, BOT_TOKEN
from models import TgUser, UserbotSession
from states import AuthSessionState
import pyrogram
from pyrogram.errors import FloodWait, SessionPasswordNeeded, PhoneNumberInvalid, PhoneCodeExpired, PhoneCodeInvalid

# client = pyrogram.Client("asd", api_id="14905013", api_hash="c4745519f27a758ecd7c81d0f5c8ec50")
# client.run()


@dp.callback_query_handler(text_contains="|usessions", state="*")
async def _(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]
    user = TgUser.objects.get({'_id': c.from_user.id})
    
    if action == "main":
        sessions = UserbotSession.objects.raw({'owner_id': user.user_id})
        await c.message.answer("Выберите сессию или добавьте новую", reply_markup=Keyboards.USessions.main(sessions))
        await AuthSessionState.session_name.set()
    if action == "new":
        await c.message.answer("✏️ Введите имя сессии:")
        await AuthSessionState.session_name.set()
        
async def sendCode(message: Message, state: FSMContext):
    global pyrogram_clients
    stateData = await state.get_data()
    
    # Создаем новый экземпляр Pyrogram клиента
    try:
        await client.run()
        await client.initialize()
        send_code_info = await client.send_code(stateData['login'])
        await client.terminate()
        await client.disconnect()
        await state.update_data(phone_code_hash=send_code_info.phone_code_hash)
        
        pyrogram_clients.append(client)
        await message.answer("✏️ Код подтверждения был отправлен на ваш аккаунт. Введите его:")
        print(f"Отправлен код подтверждения: {send_code_info}")
    except FloodWait as e:
        await message.answer(f"⏳ Подождите {e.x} секунд.")
        return
    except PhoneNumberInvalid as e:
        await message.answer(f"⚠️ Ошибка, номер телеграм не корректен! Введите номер ещё раз:")
        await AuthSessionState.login.set()
        return

@dp.callback_query_handler(ChatTypeFilter(ChatType.PRIVATE), text_contains="|us_auth", state="*")
async def _(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]
    if action == "send_new_code":
        await sendCode(c.message, state)
        
    
@dp.message_handler(Command("auth_ub"))
async def add_session_handler(message: types.Message):
    await message.answer("✏️ Введите имя сессии:")
    await AuthSessionState.session_name.set()


@dp.message_handler(state=AuthSessionState.session_name)
async def session_name_handler(message: types.Message, state: FSMContext):
    """
    Обработчик ввода имени сессии. Создает новый экземпляр Pyrogram клиента и авторизует его.
    """
    session_name = message.text
    await state.update_data(session_name=session_name)
    await message.answer("✏️ Введите номер телефона для сессии:")
    await AuthSessionState.login.set()
    

@dp.message_handler(state=AuthSessionState.login)
async def login_handler(message: types.Message, state: FSMContext):
    """
    Обработчик ввода логина. Создает новый экземпляр Pyrogram клиента и отправляет код подтверждения.
    """
    await message.answer("⏳ Отправляю код подтверждения...")
    global pyrogram_clients
    login = message.text
    await state.update_data(login=login)

    await sendCode(message, state)

    await AuthSessionState.code.set()

@dp.message_handler(state=AuthSessionState.code)
async def code_handler(message: types.Message, state: FSMContext):
    """
    Обработчик ввода кода подтверждения. Авторизует клиента Pyrogram.
    """
    global pyrogram_clients
    user = TgUser.objects.get({"_id": message.from_user.id})
    code = message.text.strip()
    stateData = await state.get_data()
    print(f"Получен код пользователя: {code}, phone_code_hash: {stateData['phone_code_hash']}")

    client: pyrogram.Client = pyrogram_clients[-1]
#API_ID=14905013
#API_HASH=c4745519f27a758ecd7c81d0f5c8ec50
    try:
        await client.connect()
        await client.sign_in(stateData['login'], stateData['phone_code_hash'], phone_code=code)
    except SessionPasswordNeeded:
        await message.answer("✏️ Для этого аккаунта требуется двухфакторная аутентификация. Введите ваш пароль:")
        await AuthSessionState.password.set()
    except PhoneCodeExpired:
        await message.answer("⚠️ Код подтверждения истек. Повторите попытку и введите новый код:")
        await AuthSessionState.code.set()
    except PhoneCodeInvalid:
        await message.answer("⚠️ Код подтверждения указан неверно. Повторите попытку и введите код:", 
                             reply_markup=Keyboards.US_Auth.sendNewCode(stateData['login']))
        await AuthSessionState.code.set()
    except Exception as e:
        await message.answer(f"⚠️ Ошибка: <b>{e}</b>")
    else:
        UserbotSession(owner_id=user, name=stateData['session_name'], login=stateData['login']).save()
        await message.answer("✅ Сессия успешно авторизована.")
        await state.finish()

@dp.message_handler(state=AuthSessionState.password)
async def password_handler(message: types.Message, state: FSMContext):
    """
    Обработчик ввода пароля для двухфакторной аутентификации. Авторизует клиента Pyrogram.
    """
    global pyrogram_clients
    user = TgUser.objects.get({"_id": message.from_user.id})
    password = message.text
    client: pyrogram.Client = pyrogram_clients[-1]
    stateData = await state.get_data()

    try:
        await client.check_password(password)
    except Exception as e:
        await message.reply(f"Ошибка: {e}")
    else:
        UserbotSession(owner_id=user, name=stateData['session_name'], login=stateData['login'], password=password).save()
        await message.answer("✅ Сессия успешно авторизована.")
        await state.finish()