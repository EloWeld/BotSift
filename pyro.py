
import asyncio
from loader import *
from config import *


async def on_message(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text
    groups = MDB.Groups.find(chat_id=chat_id)
    for group in groups:
        if user_id in group['blacklist']:
            continue
        for x in group['words']:
            if x in text:
                fwd_msg = await bot.forward_message(group["fwd_to_chat_id"], chat_id, message.message_id)
    