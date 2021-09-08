import datetime
import time
from threading import Timer

import schedule
from loader import db, dp


# async def alarm():
#     list_of_alarm = db.select_alarm_for_users(datetime.datetime.now())
#     for item in list_of_alarm:
#         user = db.select_user(item[1])
#         date_end = datetime.date(int(user[3].split("-")[0]), int(user[3].split("-")[1]), int(user[3].split("-")[1]))
#         await dp.bot.send_message(chat_id=item[1], text=f"Ваша подписка заканчивается {date_end.strftime('%d %B %Y')}")

async def alarm():
    users = db.select_users()
    for i in users:
        await dp.bot.send_message(i[0], "Работает")


async def scheduler():
    # t = Timer(86400, alarm)
    t = Timer(30, alarm)
    t.start()

def startTimer(waitForSeconds):
    loop = asyncio.new_event_loop()
    threading.Thread(daemon=True, target=loop.run_forever).start()
    async def sleep_and_run():
        await asyncio.sleep(waitForSeconds)
        await myAsyncFunc()
    asyncio.run_coroutine_threadsafe(sleep_and_run(), loop)

async def myAsyncFunc():
    print("in my async func")

startTimer(1)
while True:
    print("e")

