from datetime import datetime, date, timedelta

import requests as requests
from aiogram import types
from aiogram.dispatcher.filters.builtin import Text, Regexp
from dateutil.relativedelta import relativedelta

from keyboards.default.main import main_keyboard, price_and_back, extend_and_back, buy_and_back, back, treal_free, \
    duration_subs, payed, try_payed
from keyboards.inline.inline import kb_with_link
from loader import dp, db

from tronapi import Tron
from tronapi import HttpProvider


# ловим главные кнопки с клавиатуры main_keyboard
@dp.message_handler(Text(equals=["Моя подписка"]))
async def show_subs_status(message: types.Message):
    user = db.select_user(message.from_user.id)
    if user:
        date_of_begin_subs = user[2].split("-")
        subs_duration = user[3]
        date_of_end_subs = date(int(date_of_begin_subs[0]), int(date_of_begin_subs[1]),
                                int(date_of_begin_subs[2])) + relativedelta(months=+subs_duration)
        await message.answer(f"Ваша подписка активна до {date_of_end_subs}", reply_markup=extend_and_back)
    else:
        await message.answer("У вас нет активной подписки", reply_markup=price_and_back)


@dp.message_handler(Text(equals=["Тарифы"]))
async def show_prices(message: types.Message):
    prices = db.select_prices()
    await message.answer(
        f"Вы можете приобрести подписку:\n1 месяц - {prices[0][2]} USDT\n4 месяца – {prices[1][2]} USDT\n6 месяцев – {prices[2][2]} USDT\n1 год – {prices[3][2]} USDT",
        reply_markup=buy_and_back)


@dp.message_handler(Text(equals=["Акции"]))
async def show_sales(message: types.Message):
    sales = db.select_sales()
    treal = db.treal_mode()
    if treal:
        if treal[0] != 0:
            date_db = treal[1].split("-")
            date_date = date(int(date_db[0]), int(date_db[1]), int(date_db[2])) + timedelta(days=14)
            await message.answer(f"У вас есть шанс бесплатно попасть в VIP группу до {date_date}",
                                 reply_markup=treal_free)
    elif sales:
        await message.answer(
            f"АКЦИЯ -{sales[0][0]}% с {sales[0][1]} по {sales[0][2]}.\n"
            f"Условия акции:\n"
            f"{sales[0][3]}",
            reply_markup=buy_and_back)
    #     "АКЦИЯ и ее условия (внизу обязательно кнопка «оплатить»
    #     и отдельный текст на оплату, также кошелек и сумма на оплату, учитывая акцию.",
    else:
        await message.answer("На данный момент нет действующих акций", reply_markup=back)


# вторичные клавиатуры
# price_and_back (Тарифы ловим выше)
@dp.message_handler(Text(equals=["Назад"]))
async def bot_back(message: types.Message):
    await message.answer("Выберите действие", reply_markup=main_keyboard)


# extend_and_back
@dp.message_handler(Text(equals=["Продлить подписку"]))
async def extend_subs(message: types.Message):
    prices = db.select_prices()
    await message.answer(
        f"Вы можете продлить подписку на:\n1 месяц - {prices[0][2]} USDT\n4 месяца – {prices[1][2]} USDT\n6 месяцев – {prices[2][2]} USDT\n1 год – {prices[3][2]} USDT",
        reply_markup=buy_and_back)


# buy_and_back
@dp.message_handler(Text(equals=["Оплатить"]))
async def buy_subs(message: types.Message):
    await message.answer("Выберите вариант подписки", reply_markup=duration_subs)


# treal_free
@dp.message_handler(Text(equals=["Вступить в VIP"]))
async def get_free_treal(message: types.Message):
    await message.answer("Вы можете подписаться на VIP канал, а также вступить в VIP чат", reply_markup=kb_with_link())


# duration_subs
@dp.message_handler(Text(equals=["1 месяц", "4 месяца", "6 месяцев", "1 год"]))
async def buy_subs(message: types.Message):
    db.add_user(message.from_user.id, message.text)
    price = 150  # взять с базы
    await message.answer(f"Переведите {price} USDT на TRC20 кошелек", reply_markup=payed)
    await message.answer("TCdBe2LZkaP9GWmksDBwCxiJQ1SjoagTbU")


# payed
@dp.message_handler(Text(equals=["Оплатил"]))
async def buy_subs(message: types.Message):
    await message.answer(
        "Для проверки оплаты скопируйте сюда, пожалуйста, хеш своей трансакции и отправьте мне сообщением",
        reply_markup=payed)


hash_pattern = r"^[a-zA-Z0-9]+$"


# ловим хеш и проверяем оплату
@dp.message_handler(Regexp(hash_pattern))
async def hash_transaction(message: types.Message):
    # пример hash b6d8106f9e91de59a74f8219aa527cc787e732b25e4d83787bc37acec461bba5
    # кошелек TCdBe2LZkaP9GWmksDBwCxiJQ1SjoagTbU
    # hex кошелька 411d1eebad3bf7fc31695bf514693e613f2f36e83e
    try:
        response = check_hash(message.text)
        if response.get("raw_data").get("contract")[0].get("parameter").get("value").get("contract_address") != None:
            address = response.get("raw_data").get("contract")[0].get("parameter").get("value").get("contract_address")
        else:
            address = response.get("raw_data").get("contract")[0].get("parameter").get("value").get("to_address")

        response_status = response['ret'][0]['contractRet']
        if response_status == "SUCCESS" and address == "411d1eebad3bf7fc31695bf514693e613f2f36e83e":
            kb_subs = await kb_with_link()
            await message.answer("Ваша оплата прошла успешно!", reply_markup=main_keyboard)
            await message.answer("Вот ваши ссылки для доступа", reply_markup=kb_subs)
            now = datetime.now()
            db.edit_user_subs(message.from_user.id, now.strftime("%Y-%m-%d"))
            # записать когда напомнить
            # при появлении в подписчиках чата и группы удалить ссылки вступления
        elif response_status == "SUCCESS" and address != "411d1eebad3bf7fc31695bf514693e613f2f36e83e":
            await message.answer(
                f"Этот платеж предназначен для другого кошелька, "
                f"отправьте платеж на кошелек TCdBe2LZkaP9GWmksDBwCxiJQ1SjoagTbU",
                reply_markup=try_payed)
        else:
            await message.answer("Ваша трансакция не прошла еще, ждем подтверждения операции", reply_markup=try_payed)


    except ValueError:
        await message.answer("Такой трансакции не существует, проверьте еще раз хеш трансакции",
                             reply_markup=try_payed)


def check_hash(hash_trans):
    full_node = HttpProvider('https://api.trongrid.io')
    solidity_node = HttpProvider('https://api.trongrid.io')
    event_server = HttpProvider('https://api.trongrid.io')
    tron = Tron(full_node=full_node,
                solidity_node=solidity_node,
                event_server=event_server)

    result = tron.trx.get_transaction(hash_trans)
    return result
