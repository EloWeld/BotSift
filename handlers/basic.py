import asyncio
from aiogram import Bot, Dispatcher, types
from etc.keyboards import Keyboards
from loader import *
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.types import *
from config import API_ID, API_HASH, BOT_TOKEN
from models import TgUser
from states import AuthSessionState


@dp.callback_query_handler(text_contains="|main", state="*")
async def _(c: CallbackQuery, state: FSMContext):
    # Send welcome
    user = TgUser.objects.get({'_id': c.from_user.id})
    await c.message.edit_text("Меню", reply_markup=Keyboards.startMenu(user))


@dp.callback_query_handler(text_contains="cancel_popup", state="*")
async def _(c: CallbackQuery, state: FSMContext):
    await c.message.delete()


# Start command
@dp.message_handler(commands=["start"], state="*")
async def start_command(message: types.Message, state: FSMContext=None):
    if state:
        await state.finish()
        
    if message.chat.type in [types.ChatType.SUPERGROUP, types.ChatType.GROUP]:
        await message.answer(f"ℹ️ ChatID этой группы: <code>{message.chat.id}</code>")
        return
    try:
        user = TgUser.objects.get({'_id': message.from_user.id})
    except TgUser.DoesNotExist:
        user = TgUser(message.from_user.id, is_authenticated = False)

    # User exists already
    user.first_name = message.from_user.first_name
    user.last_name = message.from_user.last_name
    user.username = message.from_user.username
    user.save()

    # Send welcome
    if user.is_authenticated:
        await bot.send_message(chat_id=message.chat.id, text="Привет! Я твой бот.", reply_markup=Keyboards.startMenu(user))
    else:
        await message.answer("⚠️ Вы не авторизованы. Пожалуйста, введите секретный ключ:")

    # Set bot commands
    await bot.set_my_commands([
        BotCommand("start", "Презапуск бота"),
        BotCommand("help", "Помощь")
    ])


# Get statistics
@dp.message_handler(commands=["stats"], chat_type=ChatType.PRIVATE)
async def get_stats(message: types.Message):
    chat_id = message.chat.id

    count = await db.get_stats(chat_id)
    await message.reply(f"Статистика: {count} сообщений.")

# Get help


@dp.message_handler(commands=["help"], chat_type=ChatType.PRIVATE)
async def help_command(message: types.Message):
    help_text = """
Команды для управления ботом:

/all_ub - Выводит список всех доступных user-ботов
/auth_ub - Авторизирует нового user-бота

/all_gps - Выводит список всех групп
/add_gp - Добавляет группу

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
