from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from data.config import CHANNEL_ID, GROUP_ID
from loader import dp, db


async def generate_channel_link(ID):
    url_channel = await dp.bot.create_chat_invite_link(chat_id=ID)
    # print(url_channel.invite_link)
    return url_channel.invite_link


async def kb_with_link(telegram_id):
    channel_link = await generate_channel_link(CHANNEL_ID)
    group_link = await generate_channel_link(GROUP_ID)
    db.add_used_link(telegram_id, channel_link)
    db.add_used_link(telegram_id, group_link)
    free_vip_subs = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Вступить в VIP канал", url=channel_link)
        ],
        [
            InlineKeyboardButton(text="Вступить в VIP чат", url=group_link)
        ]
    ])
    return free_vip_subs

async def kb_with_sales():
    all_sales = db.select_sales()
    sales = InlineKeyboardMarkup()
    for item in all_sales:
        sales.add(InlineKeyboardButton(text=f"{item[0]}% с {item[1]} по {item[2]}", callback_data="del#"+item[1]))
    return sales

async def kb_months():
    months = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="1 месяц", callback_data="month#1")
        ],
        [
            InlineKeyboardButton(text="4 месяца", callback_data="month#4")
        ],
        [
            InlineKeyboardButton(text="6 месяцев", callback_data="month#6")
        ],
        [
            InlineKeyboardButton(text="1 год", callback_data="month#12")
        ]
    ])
    return months