import asyncio
from handlers import *

async def main_async():
    from aiogram import executor
    from loader import dp

    await dp.start_polling()


def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_async())


if __name__ == "__main__":
    start_bot()