
import asyncio
from aiogram import Bot, Dispatcher, types
from etc.keyboards import Keyboards
from loader import *
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import *
from config import API_ID, API_HASH, BOT_TOKEN
from models import TgGroup, TgUser
from states import AddGroupState

        

@dp.callback_query_handler(text_contains="|groups", state="*")
async def _(c: CallbackQuery, state: FSMContext):
    action = c.data.split(":")[1]
    user = TgUser.objects.get({'_id': c.from_user.id})
    
    if action == "main":
        sessions = TgGroup.objects.raw({'owner_id': user.user_id})
        await c.message.answer("Выберите сессию или добавьте новую", reply_markup=Keyboards.USessions.main(sessions))
    if action == "new":
        await c.message.answer("✏️ Введите имя группы:")
        await AddGroupState.name.set()
    

@dp.message_handler(state=AddGroupState.name)
async def session_name_handler(message: types.Message, state: FSMContext):
    session_name = message.text
    await state.update_data(session_name=session_name)
    await message.answer("✏️ Введите CHAT ID группы:")
    await AddGroupState.chatIDs.set()    

@dp.message_handler(state=AddGroupState.chatID)
async def session_name_handler(message: types.Message, state: FSMContext):
    session_name = message.text
    await state.update_data(session_name=session_name)
    await message.answer("✏️ Введите CHAT ID группы:")
    await AddGroupState.chatIDs.set()
