import locale
# from datetime import datetime, date, timedelta
import datetime

from aiogram import types
from aiogram.dispatcher.filters.builtin import Text, Regexp
from dateutil.relativedelta import relativedelta

from keyboards.default.main import main_keyboard, price_and_back, extend_and_back, buy_and_back, back, treal_free, \
    duration_subs, payed, try_payed, buy_with_sale_and_back, duration_subs_sale
from keyboards.inline.inline import kb_with_link
from loader import dp, db

from tronapi import Tron
from tronapi import HttpProvider

locale.setlocale(locale.LC_ALL, "")


# ловим главные кнопки с клавиатуры main_keyboard
@dp.message_handler(Text(equals=["Моя подписка"]))
async def show_subs_status(message: types.Message):
    user = db.select_user(message.from_user.id)
    if user:
        date_end = datetime.date(int(user[3].split("-")[0]), int(user[3].split("-")[1]), int(user[3].split("-")[1]))
        await message.answer(f"Ваша подписка активна до {date_end.strftime('%d %B %Y')}",
                             reply_markup=extend_and_back)
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
    now = datetime.datetime.now()
    # если включен триал и сегодняшняя дата не меньше даты начала триала для всех
    # да, я не хотела писать в переменную, да некрасиво, но да работает)))
    if treal and now >= datetime.datetime(int(treal[1].split("-")[0]), int(treal[1].split("-")[1]),
                                          int(treal[1].split("-")[2])):
        if treal[0] != 0:
            date_db = treal[1].split("-")
            date_date = datetime.datetime(int(date_db[0]), int(date_db[1]), int(date_db[2])) + datetime.timedelta(
                days=14)
            await message.answer(f"У вас есть шанс бесплатно попасть в VIP группу до {date_date.strftime('%-d %B %Y')}",
                                 reply_markup=treal_free)
    # если дата текущая больше даты начала акции и меньше даты окончания акции
    elif sales and now >= datetime.datetime(int(sales[0][1].split("-")[0]), int(sales[0][1].split("-")[1]),
                                            int(sales[0][1].split("-")[2])) and now <= datetime.datetime(
        int(sales[0][2].split("-")[0]),
        int(sales[0][2].split("-")[1]),
        int(sales[0][2].split("-")[2])):
        prices = db.select_prices()
        await message.answer(
            f"АКЦИЯ -{sales[0][0]}% с {sales[0][1]} по {sales[0][2]}.\n"
            f"Условия акции:\n"
            f"{sales[0][3]}")
        await message.answer(
            f"Акционные цены на подписку:\n1 месяц - {prices[0][2] - (prices[0][2] * sales[0][0]) / 100} USDT\n4 месяца – {prices[1][2] - (prices[1][2] * sales[0][0]) / 100} USDT\n6 месяцев – {prices[2][2] - (prices[0][2] * sales[0][0]) / 100} USDT\n1 год – {prices[3][2] - (prices[0][2] * sales[0][0]) / 100} USDT",
            reply_markup=buy_with_sale_and_back)
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
    user = db.select_user(message.from_user.id)
    if user:
        db.edit_user_duration_subs(message.from_user.id, message.text)
    else:
        db.add_user(message.from_user.id, message.text)
    price = db.select_price(message.text)
    await message.answer(f"Переведите {price[0]} USDT на TRC20 кошелек", reply_markup=payed)
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
            user = db.select_user(message.from_user.id)
            date = ""
            if user[2]:
                date_from_db = user[3].split("-")
                date = datetime.datetime(int(date_from_db[0]), int(date_from_db[1]), int(date_from_db[2]))
            else:
                date = datetime.datetime.now()
            db.edit_user_subs(message.from_user.id, date.strftime("%Y-%m-%d"))
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


# buy_with_sale_and_back
@dp.message_handler(Text(equals=["Оплатить со скидкой"]))
async def buy_subs(message: types.Message):
    await message.answer("Выберите вариант подписки", reply_markup=duration_subs_sale)


# duration_subs_sale
@dp.message_handler(
    Text(equals=["1 месяц со скидкой", "4 месяца со скидкой", "6 месяцев со скидкой", "1 год со скидкой"]))
async def buy_subs(message: types.Message):
    user = db.select_user(message.from_user.id)
    if user:
        db.edit_user_duration_subs(message.from_user.id, message.text)
    else:
        db.add_user(message.from_user.id, message.text)
    price = db.select_price(message.text)
    await message.answer(f"Переведите {price[0]} USDT на TRC20 кошелек", reply_markup=payed)
    await message.answer("TCdBe2LZkaP9GWmksDBwCxiJQ1SjoagTbU")
