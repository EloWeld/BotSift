import asyncio
import json
from typing import List

import requests
from config import API_HASH, API_ID, BOT_TOKEN
from etc.keyboards import Keyboards
from models import UserbotSession, TgGroup
from pyrogram import Client
import pyrogram
import loguru


def userbotSessionToPyroClient(session: UserbotSession) -> Client:
    return Client(
            name=session.name,
            session_string=session.string_session,
            api_id=API_ID,
            api_hash=API_HASH,
        )

def start_pyro_client(_, stop_event, usession: UserbotSession):
    async def run_client():
        client = userbotSessionToPyroClient(usession)
        
        def checkMessage(message: pyrogram.types.Message, group: TgGroup):
            is_good_message = False
            # dont Recursion pls
            if group.chat_id == message.chat.id:
                is_good_message = False
                return False
            text = message.text if message.text is not None else message.caption if message.caption is not None else None
            if text is None:
                return False
            # Check message sender
            if str(message.from_user.id) in group.blacklist_users or message.from_user.username in group.blacklist_users:
                is_good_message = False
                return False
            # Check keywords
            for keyword in group.keywords:
                if keyword in text.lower():
                    is_good_message = True
                    break
            # Check minus words
            if is_good_message:
                for bad_keyword in group.bad_keywords:
                    if bad_keyword in text.lower():
                        is_good_message = False
                        return False
            return is_good_message
        
        @client.on_message()
        async def handle_messages(client: pyrogram.Client, message: pyrogram.types.Message):
            import traceback
            print(message)
            groups: List[TgGroup] = TgGroup.objects.all()
            for group in groups:
                is_good_message = checkMessage(message, group)
                if is_good_message:
                    try:
                        from loader import bot
                        if message.chat.username:
                            linkToMessage = f"https://t.me/{message.chat.username}/{message.id}"
                        else:
                            linkToMessage = None
                        # Set your Bot Token here
                        bot_token = BOT_TOKEN

                        # Send message using requests
                        text = f"В группе <b>{message.chat.title}</b> есть отобранное сообщение\n\n{message.text.html if message.text else message.caption.html}\n\n<b>Кто: {message.from_user.id} {message.from_user.first_name} {message.from_user.last_name} @{message.from_user.username}</b>"
                        chat_id = group.chat_id
                        inline_keyboard_markup = {
                            "inline_keyboard": [
                                [
                                    {
                                        "text": "Go to Message",
                                        "url": linkToMessage
                                    }
                                ]
                            ]
                        }

                        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                        payload = {
                            "chat_id": chat_id,
                            "text": text,
                           "reply_markup": json.dumps(inline_keyboard_markup),
                            "parse_mode": "HTML",
                        }

                        response = requests.post(url, data=payload)

                        if response.status_code == 200:
                            loguru.logger.success(f"Forward message {message.id} from chat {message.chat.id}")
                        else:
                            loguru.logger.error(f"Failed to send message {message.id} from chat {message.chat.id}; status code: {response.status_code}")

                        loguru.logger.success(f"Forward message {message.id} from chat {message.chat.id}")
                        group.forwarded_msgs += [dict(from_chat=message.chat.id, message_id=message.id, message_text=message.text, sender_id=message.from_user.id, sender_username=message.from_user.username)]
                        group.save()
                    except Exception as e:
                        loguru.logger.error(f"Can't forward message {message.id} from chat {message.chat.id}; error: {e}, traceback: {traceback.format_exc()}")
                        #await client.send_message(group.chat_id, f"Can't forward message {message.id} from chat {message.chat.id}; error: {e}, traceback: {traceback.format_exc()}")
                    
        
        # Start the client
        await client.start()
        while not stop_event.is_set():
            # Check if session is overwritten
            current_session: UserbotSession = UserbotSession.objects.get({"_id": usession.id})
            if current_session.string_session != usession.string_session:
                break

            await asyncio.sleep(1)  # Adjust sleep time as needed

        await client.stop()
    asyncio.run(run_client())

