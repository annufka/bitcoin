from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from data.config import ADMINS
from filters.type_chat import IsPrivate
from keyboards.default.main import main_keyboard, admins_main_kb
from loader import dp


@dp.message_handler(IsPrivate(), CommandStart())
async def bot_start(message: types.Message):
    # админ
    if str(message.from_user.id) in ADMINS:
        await message.answer(
            f"Привет, админ! Выбери, что ты хочешь настроить", reply_markup=admins_main_kb)
    # обычный пользователь
    else:
        await message.answer(
            f"Привет, {message.from_user.full_name}! Выбери, пожалуйста, действие ниже для продолжения разговора 😉",
            reply_markup=main_keyboard)
    # await message.answer(
    #     f"Привет, {message.from_user.full_name}! Выбери, пожалуйста, действие ниже для продолжения разговора 😉",
    #     reply_markup=main_keyboard)