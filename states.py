from aiogram.dispatcher.filters.state import State, StatesGroup

class AuthSessionState(StatesGroup):
    session_name = State()
    login = State()
    code = State()
    password = State()