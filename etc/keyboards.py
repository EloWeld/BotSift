from typing import List, Union
from aiogram.types import \
    ReplyKeyboardMarkup as Keyboard, \
    KeyboardButton as Button, \
    InlineKeyboardMarkup as IKeyboard, \
    InlineKeyboardButton as IButton

from models import TgGroup, UserbotSession

class Keyboards:
    class US_Auth:
        @staticmethod
        def sendNewCode(session_name):
            k = IKeyboard()
            k.row(IButton("Прислать новый", callback_data=f"|us_auth:send_new_code:{session_name}"))
            return k
        
    class USessions:
        @staticmethod
        def main(sessions: List[UserbotSession]):
            k = IKeyboard()
            for session in sessions:
                k.row(IButton(session.name, callback_data=f"|usessions:see:{session.id}"))
            k.row(IButton("Добавить", callback_data=f"|usessions:new"))
            k.row(IButton("Назад", callback_data=f"main"))
            return k
        
    class Groups:
        @staticmethod
        def main(groups: List[TgGroup]):
            k = IKeyboard()
            for group in groups:
                k.row(IButton(group.name, callback_data=f"|groups:see:{group.id}"))
            k.row(IButton("Добавить", callback_data=f"|groups:new"))
            k.row(IButton("Назад", callback_data=f"main"))
            return k
    
    @staticmethod
    def startMenu(user):
        k = IKeyboard()
        k.row(IButton("Группы", callback_data=f"|groups:main"))
        k.row(IButton("Юзерботы", callback_data=f"|usessions:main"))
        return k
            
        