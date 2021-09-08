from aiogram import types

from filters.type_chat import IsGroup
from loader import dp


@dp.message_handler(IsGroup(), content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def new_member(message: types.Message):
    pass
    # members = ", ".join([m.get_mention(as_html=True) for m in message.new_chat_members])
    # await message.reply(f"Привет, {members}.")