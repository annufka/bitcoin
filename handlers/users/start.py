import sqlite3
import time

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from data.config import ADMINS
from filters.type_chat import IsPrivate
from keyboards.default.main import main_keyboard, admins_main_kb
from loader import dp, db


@dp.message_handler(IsPrivate(), CommandStart())
async def bot_start(message: types.Message):
    # админ
    if str(message.from_user.id) in ADMINS:
        await message.answer(
            f"Привет, админ! Выбери, что ты хочешь настроить", reply_markup=admins_main_kb)
    # обычный пользователь
    # танцы с бубнами нужны, чтобы пользователей по юзернейму добавить, потому что ид у меня нет.
    else:
        user = db.select_user(message.from_user.id)
        if not user:
            try:
                user = db.select_user_by_username(message.from_user.username)
            except sqlite3.Error:
                time.sleep(20)
                try:
                    user = db.select_user_by_username(message.from_user.username)
                except:
                    pass
            if user:
                try:
                    db.edit_user_telegram_id(message.from_user.username, message.from_user.id)
                except sqlite3.Error:
                    time.sleep(20)
                    try:
                        db.edit_user_telegram_id(message.from_user.username, message.from_user.id)
                    except:
                        db.edit_user_telegram_id(message.from_user.username, message.from_user.id)
        await message.answer(
            f"Привет, {message.from_user.full_name}! Выбери, пожалуйста, действие ниже для продолжения разговора 😉",
            reply_markup=main_keyboard)

    # await message.answer(
    #     f"Привет, {message.from_user.full_name}! Выбери, пожалуйста, действие ниже для продолжения разговора 😉",
    #     reply_markup=main_keyboard)