import asyncio
import threading
from typing import List
from loader import dp, threads
from handlers import *
from pyroProcessing import start_pyro_client



async def main_async():
    global threads
    all_sessions: List[UserbotSession] = UserbotSession.objects.all()
    threads = {}

    for usession in all_sessions:
        try:
            client = userbotSessionToPyroClient(usession)
            stop_event = threading.Event()
            
            t = threading.Thread(target=start_pyro_client, args=(client, stop_event, usession), name=f"Usebot #{client.name}")
            t.start()
            threads[usession.id] = dict(thread=t, stop_event=stop_event, client=client)
        except Exception as e:
            loguru.logger.error(f"Can't start userbot session {usession.name}. Error: {e}, traceback: {traceback.format_exc()}")

    await dp.start_polling()

    for t in threads:
        t.join()


def start_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_async())


if __name__ == "__main__":
    start_bot()