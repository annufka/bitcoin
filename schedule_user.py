import asyncio
import datetime

from loader import db, dp


async def startTimer(waitForSeconds):
    while True:
        await asyncio.sleep(waitForSeconds)
        list_of_alarm = db.select_alarm_for_users(datetime.datetime.now())
        for item in list_of_alarm:
            user = db.select_user(item[1])
            date_end = datetime.date(int(user[3].split("-")[0]), int(user[3].split("-")[1]), int(user[3].split("-")[1]))
            await dp.bot.send_message(chat_id=item[1],
                                      text=f"Ваша подписка заканчивается {date_end.strftime('%d %B %Y')}")
