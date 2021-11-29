import asyncio
import datetime
import os
import sqlite3
import time

import openpyxl
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram.types import CallbackQuery

from data.config import CHANNEL_ID, GROUP_ID
from filters.type_chat import IsPrivate
from keyboards.inline.inline import kb_with_sales, kb_months
from loader import dp, db
from states.admin_state import EnterPrice, EnterSale, IdChannel


# Сменить стоимость за {}
@dp.message_handler(IsPrivate(), Text(equals=["Сменить стоимость подписки"]), state=None)
async def edit_price(message: types.Message):
    months = await kb_months()
    await message.answer("Выберите тип подписки", reply_markup=months)
    await EnterPrice.duration.set()


@dp.callback_query_handler(Text(contains="month#"), state=EnterPrice.duration)
async def edit_price(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(duration=call.data.split("#")[1])
    await call.message.edit_text(f"Введите новую стоимость подписки на {call.data.split('#')[1]} " + "мес." if int(
        call.data.split('#')[1]) < 12 else "год", reply_markup=None)
    await EnterPrice.next()


@dp.message_handler(state=EnterPrice.enter_price)
async def save_price(message: types.Message, state: FSMContext):
    await state.update_data(enter_price=message.text)
    data = await state.get_data()
    try:
        db.edit_price(data["duration"], data["enter_price"])
        await message.answer("Записал")
        await state.finish()
    except sqlite3.Error:
        time.sleep(20)
        try:
            db.edit_price(data["duration"], data["enter_price"])
            await message.answer("Записал")
            await state.finish()
        except:
            await message.answer("Заскриньте нашу переписку и отправьте программисту, что-то пошло не так при редактировании стоимости подписки")


# Включить пробные две недели для всех пользователей
@dp.message_handler(IsPrivate(), Text(equals=["Включить пробные две недели для всех пользователей"]))
async def edit_price(message: types.Message):
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
    try:
        db.treal_on(tomorrow.strftime("%Y-%m-%d"))
        await message.answer("Пробная подписка для всех пользователей будет включена завтра")
    except sqlite3.Error:
        time.sleep(20)
        try:
            db.treal_on(tomorrow.strftime("%Y-%m-%d"))
            await message.answer("Пробная подписка для всех пользователей будет включена завтра")
        except:
            await message.answer("Заскриньте нашу переписку и отправьте программисту, что-то пошло не так при включении пробной подписки")


# Добавить акцию
@dp.message_handler(IsPrivate(), Text(equals=["Добавить акцию"]), state=None)
async def add_sale(message: types.Message):
    await message.answer("Введите размер скидки в процентах (без значка процента)")
    await EnterSale.enter_sale.set()


@dp.message_handler(state=EnterSale.enter_sale)
async def save_sale(message: types.Message, state: FSMContext):
    await state.update_data(enter_sale=message.text)
    await message.answer("Введите дату начала акции в формате год-месяц-день (например, 2021-09-03)")
    await EnterSale.next()


@dp.message_handler(state=EnterSale.enter_begin)
async def save_begin_in_calendar(message: types.Message, state: FSMContext):
    await state.update_data(enter_begin=message.text)
    await message.answer("Введите дату окончания акции в формате год-месяц-день (например, 2021-09-03)")
    await EnterSale.next()


@dp.message_handler(state=EnterSale.enter_end)
async def save_end_in_calendar(message: types.Message, state: FSMContext):
    await state.update_data(enter_end=message.text)
    await message.answer("Введите условия акции")
    await EnterSale.next()


@dp.message_handler(state=EnterSale.enter_text)
async def save_text(message: types.Message, state: FSMContext):
    await state.update_data(enter_text=message.text)
    data = await state.get_data()
    try:
        db.add_sale(data["enter_sale"], data["enter_begin"], data["enter_end"], data["enter_text"])
        await message.answer("Записал данные акции")
        await state.finish()
    except sqlite3.Error:
        try:
            time.sleep(20)
            db.add_sale(data["enter_sale"], data["enter_begin"], data["enter_end"], data["enter_text"])
            await message.answer("Записал данные акции")
            await state.finish()
        except:
            await message.answer("Заскриньте нашу переписку и отправьте программисту, что-то пошло не так при записи акции")


# Удалить акцию
@dp.message_handler(IsPrivate(), Text(equals=["Удалить акцию"]))
async def delete_sale(message: types.Message):
    sales = await kb_with_sales()
    await message.answer("Выберите акцию, которую хотите удалить\n\n", reply_markup=sales)


@dp.callback_query_handler(Text(contains="del#"))
async def delete_from_db_sale(call: CallbackQuery):
    await call.answer()
    date = (call.data.split("#")[1]).split("-")
    date_date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
    try:
        db.delete_sale(date_date)
        await call.message.edit_text(text="Вы удалили акцию", reply_markup=None)
    except sqlite3.Error:
        try:
            time.sleep(20)
            db.delete_sale(date_date)
            await call.message.edit_text(text="Вы удалили акцию", reply_markup=None)
        except:
            await call.message.answer("Заскриньте нашу переписку и отправьте программисту, что-то пошло не так при удалении акции")


# надо чтобы один раз узнать ид канала
# @dp.message_handler(IsPrivate(),Command("id"), state=None)
# async def id_channel(message: types.Message):
#     await message.answer("Перешлите любое сообщение из чата или канала, чтобы я мог вернуть вам id")
#     await IdChannel.forward_message.set()
#
#
# @dp.message_handler(state=IdChannel.forward_message)
# async def forwarded_message(message: types.Message, state: FSMContext):
#     result_id = message.forward_from_chat.id
#     await message.answer(f"{result_id}")
#     await state.finish()
#
#
# @dp.message_handler(Command("id_group"))
# async def chat(member: types.ChatMemberUpdated):
#     await dp.bot.send_message(chat_id=312038680, text=f"{member.chat.id}")


# Сформировать список подписчиков
@dp.message_handler(IsPrivate(), Text(equals=["Сформировать список подписчиков"]))
async def create_excel(message: types.Message):
    await message.answer("Подождите пару минут, я сформирую отчет")

    try:
        info_for_file = db.all_users()
    except sqlite3.Error:
        time.sleep(20)
        info_for_file = db.all_users()
    except:
        await message.answer("Даже если файл сформируется, скорее всего он будет пуст, так как произошла ошибка. Напиши программисту и скинь скрин.")

    wb = openpyxl.Workbook()
    wb.create_sheet(title='Пользователи', index=0)
    sheet = wb['Пользователи']
    sheet.append(["Username", "Пробная подписка", "Дата начала подписки", "Дата окончания подписки", "Длительность подписки"])
    for row in info_for_file:
        data_row = [row[1],]
        if row[2] == 0:
            data_row.append("Да")
        elif row[2] == 1:
            data_row.append("Нет")
        else:
            data_row.append("Еще не закончил регистрацию")
        data_row.append(row[3])
        data_row.append(row[4])
        if row[5] == 1:
            data_row.append("1 месяц")
        elif row[5] == 2:
            data_row.append("4 месяца")
        elif row[5] == 3:
            data_row.append("6 месяцев")
        elif row[5] == 4:
            data_row.append("1 год")
        sheet.append(data_row)
    day = datetime.datetime.now()
    wb.save(f'users-{day.strftime("%Y-%m-%d")}.xlsx')

    with open(f'users-{day.strftime("%Y-%m-%d")}.xlsx', 'rb') as file:
        await dp.bot.send_document(chat_id=message.from_user.id, document=file)

    if os.path.exists(f'users-{day.strftime("%Y-%m-%d")}.xlsx'):
        os.remove(f'users-{day.strftime("%Y-%m-%d")}.xlsx')
    else:
        pass


@dp.message_handler(Command("members"))
async def get_members(message: types.Message):
    from telethon import TelegramClient, sync

    api_id = 18180086
    api_hash = '32bda2f7e77875c152b12539e3868df7'

    client = TelegramClient(None, api_id, api_hash)
    client = TelegramClient('+380930159293', api_id, api_hash)
    client.start()

    if not client.is_user_authorized():
        client.send_code_request('+380930159293')
        client.sign_in('+380930159293', input('Enter the code: '))

    # get all the channels that I can access
    channels = {d.entity.username: d.entity
                for d in await client.get_dialogs()
                if d.is_channel}

    # choose the one that I want list users from
    channel = channels["тест"]

    # get all the users and print them
    for u in await client.get_participants(channel):
        print(u.id, u.first_name, u.last_name, u.username)
