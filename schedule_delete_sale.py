import asyncio
import datetime

from data.config import GROUP_ID, CHANNEL_ID
from loader import db, dp


async def deleteSale(waitForSeconds):
    while True:
        await asyncio.sleep(waitForSeconds)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        sales = db.select_sales_with_date(yesterday.strftime("%Y-%m-%d"))
        for sale in sales:
            db.delete_sale(sale[1])

async def deleteTreal(waitForSeconds):
    while True:
        await asyncio.sleep(waitForSeconds)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        treal = db.select_treal_with_date(yesterday.strftime("%Y-%m-%d"))
        if treal:
            db.treal_off()
            users = db.select_users_with_treal(yesterday.strftime("%Y-%m-%d"))
            for user in users:
                await dp.bot.kick_chat_member(chat_id=GROUP_ID, user_id=user[0])
                await dp.bot.kick_chat_member(chat_id=CHANNEL_ID, user_id=user[0])
