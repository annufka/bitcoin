import asyncio
import datetime

from data.config import GROUP_ID, CHANNEL_ID
from loader import db, dp


async def startTimer(waitForSeconds):
    while True:
        await asyncio.sleep(waitForSeconds)
        list_of_alarm = db.select_alarm_for_users(datetime.datetime.now())
        for item in list_of_alarm:
            user = db.select_user(item[1])
            date_end = datetime.date(int(user[3].split("-")[0]), int(user[3].split("-")[1]), int(user[3].split("-")[2]))
            await dp.bot.send_message(chat_id=item[1],
                                      text=f"Ваша подписка заканчивается {date_end.strftime('%d %B %Y')}")

async def kick_user(waitForSeconds):
    while True:
        await asyncio.sleep(waitForSeconds)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        users = db.select_users_with_date(yesterday.strftime("%Y-%m-%d"))
        for user in users:
            await dp.bot.kick_chat_member(chat_id=GROUP_ID, user_id=user[0])
            await dp.bot.kick_chat_member(chat_id=CHANNEL_ID, user_id=user[0])
            db.delete_user_all_null(user[0])