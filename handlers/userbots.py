import asyncio
import threading
import traceback
from uuid import uuid4
from aiogram import Bot, Dispatcher, types
import loguru
from etc.keyboards import Keyboards
from loader import *
from aiogram.dispatcher.filters import Command, ChatTypeFilter
from aiogram.dispatcher import FSMContext
from aiogram.types import *
from config import API_ID, API_HASH, BOT_TOKEN
from models import TgUser, UserbotSession
from pyroProcessing import start_pyro_client, userbotSessionToPyroClient
from states import AuthSessionState
import pyrogram
from pyrogram.errors import FloodWait, SessionPasswordNeeded, PhoneNumberInvalid, PhoneCodeExpired, PhoneCodeInvalid

async def sendUb(msg: Message, ubot, edit=False):
    func = msg.answer if not edit else msg.edit_text
    await func(f"Юзербот <code>{ubot.name}</code>\n"
                            f"Номер телефона: <code>{ubot.login}</code>\n\n"
                            f"Строка авторизации: <code>{ubot.string_session}</code>", reply_markup=Keyboards.USessions.showUSession(ubot))

@dp.callback_query_handler(text_contains="|usessions", state="*")
async def _(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]
    user = TgUser.objects.get({'_id': c.from_user.id})

    if action == "main":
        sessions = UserbotSession.objects.all()
        await c.message.edit_text("Выберите сессию или добавьте новую", reply_markup=Keyboards.USessions.main(sessions))
    if action == "new":
        await c.answer()
        await c.message.answer("⚠️ Внимание! Не авторизируйте аккаут через который общаетесь с ботом! Телеграм заблокирует разглашение кода для входа из-за чего выполнить вход не удасться!\n\n✏️ Введите имя сессии:")
        await AuthSessionState.session_name.set()
    if action == "see":
        us = UserbotSession.objects.get({'_id': c.data.split(":")[2]})
        await sendUb(c.message, us, True)
        await c.answer()
    if action == "reauthorize":
        us = UserbotSession.objects.get({'_id': c.data.split(":")[2]})
        await c.message.answer("⚠️ Внимание! Не авторизируйте аккаут через который общаетесь с ботом! Телеграм заблокирует разглашение кода для входа из-за чего выполнить вход не удасться!\n\n✏️ Введите НОВОЕ имя сессии:")
        await state.update_data(editing_us_id=us.id)
        await AuthSessionState.session_name.set()
        


async def sendCode(message: Message, state: FSMContext):
    global pyrogram_clients
    stateData = await state.get_data()

    # Создаем новый экземпляр Pyrogram клиента

    client: pyrogram.Client = pyrogram.Client(":memory:", api_id=API_ID, api_hash=API_HASH, in_memory=True)

    try:
        await client.connect()
        send_code_info = await client.send_code(stateData['login'])
        await state.update_data(phone_code_hash=send_code_info.phone_code_hash)

        pyrogram_clients.append(client)
        await message.answer("✏️ Код подтверждения был отправлен на ваш аккаунт. Введите его:")
        print(
            f"Отправлен код подтверждения: {send_code_info}")
    except FloodWait as e:
        await message.answer(f"⏳ Подождите {e} секунд.")
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
    await message.answer("⚠️ Внимание! Не авторизируйте аккаут через который общаетесь с ботом! Телеграм заблокирует разглашение кода для входа из-за чего выполнить вход не удасться!\n\n✏️ Введите имя сессии:")
    await AuthSessionState.session_name.set()


@dp.message_handler(state=AuthSessionState.session_name)
async def session_name_handler(message: types.Message, state: FSMContext):
    """
    Обработчик ввода имени сессии. Создает новый экземпляр Pyrogram клиента и авторизует его.
    """
    session_name = message.text[:25]
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
    login = message.text.replace(' ', '').replace('-', '')
    await state.update_data(login=login)

    await sendCode(message, state)

    await AuthSessionState.code.set()


@dp.message_handler(state=AuthSessionState.code)
async def code_handler(message: types.Message, state: FSMContext):
    """
    Обработчик ввода кода подтверждения. Авторизует клиента Pyrogram.
    """
    global pyrogram_clients

    code = message.text.strip()
    stateData = await state.get_data()
    print(f"Получен код пользователя: {code}, phone_code_hash: {stateData['phone_code_hash']}")

    client: pyrogram.Client = pyrogram_clients[-1]
    try:
        await client.sign_in(stateData['login'], stateData['phone_code_hash'], phone_code=code)
    except SessionPasswordNeeded:
        hint = await client.get_password_hint()
        await message.answer(f"✏️ Для этого аккаунта требуется двухфакторная аутентификация.\n\nПодсказка для пароля: <code>{hint}</code>\n\nВведите ваш пароль:")
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
        await authSession(message, client, state)


@dp.message_handler(state=AuthSessionState.password)
async def password_handler(message: types.Message, state: FSMContext):
    """
    Обработчик ввода пароля для двухфакторной аутентификации. Авторизует клиента Pyrogram.
    """
    global pyrogram_clients
    password = message.text
    client: pyrogram.Client = pyrogram_clients[-1]

    try:
        await client.check_password(password)
    except Exception as e:
        await message.reply(f"⚠️ Ошибка: <b>{e}</b>")
    else:
        await authSession(message, client, state)


async def authSession(message: Message, client, state):
    global threads
    user: TgUser = TgUser.objects.get({"_id": message.from_user.id})
    
    stateData = await state.get_data()
    string_session = await client.export_session_string()
    if 'editing_us_id' in stateData:
        us: UserbotSession = UserbotSession.objects.get({"_id":stateData['editing_us_id']})
        us.name = stateData['session_name']
        us.string_session = string_session
        us.login = stateData['login']
        us.save()
        # Try to stop current userbot client
        try:
            threads[us.id]['stop_event'].set()
        except Exception as e:
            loguru.logger.error(f"Can't stop current userbot client, error: {e}, traceback: {traceback.format_exc()}")
        
    else:
        us = UserbotSession(id=str(uuid4())[:12], owner_id=user.user_id, name=stateData['session_name'],
                   login=stateData['login'], string_session=string_session).save()
    await message.answer("✅ Сессия успешно авторизована.")
    await state.finish()
    await dp.storage.reset_data(chat=user.user_id)
    await sendUb(message, us, False)
    await client.disconnect()
    
    try:
        client = userbotSessionToPyroClient(us)
        stop_event = threading.Event()
        
        t = threading.Thread(target=start_pyro_client, args=(client, stop_event, us), name=f"Usebot #{client.name}")
        t.start()
        threads[us.id] = dict(thread=t, stop_event=stop_event, client=client)
    
    except Exception as e:
        loguru.logger.error(f"Can't start userbot session {us.name}. Error: {e}, traceback: {traceback.format_exc()}")
