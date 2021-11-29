import locale
# from datetime import datetime, date, timedelta
import datetime
import sqlite3
import time

import requests
from aiogram import types
from aiogram.dispatcher.filters.builtin import Text, Regexp
from binance import client, Client
from dateutil.relativedelta import relativedelta

from data.config import GROUP_ID, CHANNEL_ID, ADMINS, API_KEY, API_SECRET
from filters.type_chat import IsPrivate
from keyboards.default.main import main_keyboard, price_and_back, extend_and_back, buy_and_back, back, treal_free, \
    duration_subs, payed, try_payed, buy_with_sale_and_back, duration_subs_sale
from keyboards.inline.inline import kb_with_link
from loader import dp, db

from tronapi import Tron
from tronapi import HttpProvider

locale.setlocale(locale.LC_ALL, "")


# ловим главные кнопки с клавиатуры main_keyboard
@dp.message_handler(IsPrivate(), Text(equals=["Моя подписка"]))
async def show_subs_status(message: types.Message):
    try:
        user = db.select_user(message.from_user.id)
    except sqlite3.Error:
        time.sleep(20)
        try:
            user = db.select_user(message.from_user.id)
        except:
            await message.answer(
                "Возникла ошибка при поиске информации о вашей подписке, попробуйте немного позже, пожалуйста.\nЕсли эта ошибка возникла несколько раз подряд, "
                "напишите админу @achibtc и скиньте скрин.", reply_markup=price_and_back)
    if user:
        try:
            date_end = datetime.date(int(user[3].split("-")[0]), int(user[3].split("-")[1]), int(user[3].split("-")[2]))
            await message.answer(f"Ваша подписка активна до {date_end.strftime('%d %B %Y')}",
                                 reply_markup=extend_and_back)
        except AttributeError:
            await message.answer("У вас нет активной подписки", reply_markup=price_and_back)
        except:
            await message.answer("Что-то пошло не так, попробуйте позже", reply_markup=price_and_back)
    else:
        await message.answer("У вас нет активной подписки", reply_markup=price_and_back)


@dp.message_handler(IsPrivate(), Text(equals=["Тарифы"]))
async def show_prices(message: types.Message):
    try:
        prices = db.select_prices()
        await message.answer(
            f"Вы можете приобрести подписку:\n1 месяц - {prices[0][2]} USDT\n4 месяца – {prices[1][2]} USDT\n6 месяцев – {prices[2][2]} USDT\n1 год – {prices[3][2]} USDT",
            reply_markup=buy_and_back)
    except sqlite3.Error:
        time.sleep(20)
        try:
            prices = db.select_prices()
            await message.answer(
                f"Вы можете приобрести подписку:\n1 месяц - {prices[0][2]} USDT\n4 месяца – {prices[1][2]} USDT\n6 месяцев – {prices[2][2]} USDT\n1 год – {prices[3][2]} USDT",
                reply_markup=buy_and_back)
        except:
            await message.answer(
                "Возникла ошибка при поиске информации о тарифах, попробуйте немного позже, пожалуйста.\nЕсли эта ошибка возникла несколько раз подряд, "
                "напишите админу @achibtc и скиньте скрин.", reply_markup=buy_and_back)


@dp.message_handler(IsPrivate(), Text(equals=["Акции"]))
async def show_sales(message: types.Message):
    sales = db.select_sales()
    treal = db.treal_mode()
    now = datetime.datetime.now()
    # если включен триал и сегодняшняя дата не меньше даты начала триала для всех
    # да, я не хотела писать в переменную, да некрасиво, но да работает)))
    if treal[0] != 0:
        if now >= datetime.datetime(int(treal[1].split("-")[0]), int(treal[1].split("-")[1]),
                                    int(treal[1].split("-")[2])):
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
@dp.message_handler(IsPrivate(), Text(equals=["Назад"]))
async def bot_back(message: types.Message):
    await message.answer("Выберите действие", reply_markup=main_keyboard)


# extend_and_back
@dp.message_handler(IsPrivate(), Text(equals=["Продлить подписку"]))
async def extend_subs(message: types.Message):
    try:
        prices = db.select_prices()
        await message.answer(
            f"Вы можете продлить подписку на:\n1 месяц - {prices[0][2]} USDT\n4 месяца – {prices[1][2]} USDT\n6 месяцев – {prices[2][2]} USDT\n1 год – {prices[3][2]} USDT",
            reply_markup=buy_and_back)
    except sqlite3.Error:
        time.sleep(20)
        try:
            prices = db.select_prices()
            await message.answer(
                f"Вы можете продлить подписку на:\n1 месяц - {prices[0][2]} USDT\n4 месяца – {prices[1][2]} USDT\n6 месяцев – {prices[2][2]} USDT\n1 год – {prices[3][2]} USDT",
                reply_markup=buy_and_back)
        except:
            await message.answer(
                "Возникла ошибка при поиске информации о тарифах, попробуйте немного позже, пожалуйста.\nЕсли эта ошибка возникла несколько раз подряд, "
                "напишите админу @achibtc и скиньте скрин.", reply_markup=buy_and_back)


# buy_and_back
@dp.message_handler(IsPrivate(), Text(equals=["Оплатить"]))
async def buy_subs(message: types.Message):
    await message.answer("Выберите вариант подписки", reply_markup=duration_subs)


# treal_free
@dp.message_handler(IsPrivate(), Text(equals=["Вступить в VIP"]))
async def get_free_treal(message: types.Message):
    try:
        db.add_treal_user(message.from_user.id, message.from_user.full_name)
        await dp.bot.unban_chat_member(chat_id=GROUP_ID, user_id=message.from_user.id)
        await dp.bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
        await message.answer("Вы можете подписаться на VIP канал, а также вступить в VIP чат",
                             reply_markup=await kb_with_link(message.from_user.id))
    except sqlite3.Error:
        time.sleep(20)
        try:
            db.add_treal_user(message.from_user.id, message.from_user.full_name)
            await dp.bot.unban_chat_member(chat_id=GROUP_ID, user_id=message.from_user.id)
            await dp.bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
            await message.answer("Вы можете подписаться на VIP канал, а также вступить в VIP чат",
                                 reply_markup=await kb_with_link(message.from_user.id))
        except:
            await message.answer(
                "Возникла ошибка при активации пробной подписки, попробуйте немного позже, пожалуйста.\nЕсли эта ошибка возникла несколько раз подряд, "
                "напишите админу @achibtc и скиньте скрин.", reply_markup=main_keyboard)

# duration_subs_sale
@dp.message_handler(IsPrivate(),
                    Text(equals=["1 месяц со скидкой", "4 месяца со скидкой", "6 месяцев со скидкой",
                                 "1 год со скидкой"]))
async def buy_subs(message: types.Message):
    user = db.select_user(message.from_user.id)
    if user:
        try:
            db.edit_user_duration_subs(message.from_user.id, message.text)
        except sqlite3.Error:
            time.sleep(20)
            try:
                db.edit_user_duration_subs(message.from_user.id, message.text)
            except:
                await message.answer(
                    "Возникла ошибка при изменении информации о вашей подписке, попробуйте немного позже, пожалуйста.\nЕсли эта ошибка возникла несколько раз подряд, "
                    "напишите админу @achibtc и скиньте скрин.", reply_markup=duration_subs)

    else:
        try:
            db.add_user(message.from_user.id, message.text, message.from_user.username if message.from_user.username else message.from_user.full_name)
        except sqlite3.Error:
            time.sleep(20)
            try:
                db.add_user(message.from_user.id, message.text, message.from_user.username if message.from_user.username else message.from_user.full_name)
            except:
                await message.answer(
                    "Возникла ошибка при добавлении вас в базу, попробуйте немного позже, пожалуйста.\nЕсли эта ошибка возникла несколько раз подряд, "
                    "напишите админу @achibtc и скиньте скрин.", reply_markup=duration_subs)
    price = db.select_price(message.text)
    sale = db.select_sales()
    await message.answer(
        f"Переведите {price[0]-(price[0]*sale[0][0]/100)} USDT на TRC20 кошелек. После оплаты нажмите кнопку 'Оплатил' и следуйте дальнейшим инструкциям",
        reply_markup=payed)
    await message.answer("TCdBe2LZkaP9GWmksDBwCxiJQ1SjoagTbU")


# duration_subs
@dp.message_handler(IsPrivate(), Text(equals=["1 месяц", "4 месяца", "6 месяцев", "1 год"]))
async def buy_subs(message: types.Message):
    try:
        user = db.select_user(message.from_user.id)
    except sqlite3.Error:
        time.sleep(20)
        try:
            user = db.select_user(message.from_user.id)
        except sqlite3.Error:
            pass
    if user:
        try:
            db.edit_user_duration_subs(message.from_user.id, message.text)
        except sqlite3.Error:
            time.sleep(20)
            try:
                db.edit_user_duration_subs(message.from_user.id, message.text)
            except:
                await message.answer(
                    "Возникла ошибка при изменении информации о вашей подписке, попробуйте немного позже, пожалуйста.\nЕсли эта ошибка возникла несколько раз подряд, "
                    "напишите админу @achibtc и скиньте скрин.", reply_markup=duration_subs)
    else:
        try:
            db.add_user(message.from_user.id, message.text, message.from_user.username if message.from_user.username else message.from_user.full_name)
        except sqlite3.Error:
            time.sleep(20)
            try:
                db.add_user(message.from_user.id, message.text, message.from_user.username if message.from_user.username else message.from_user.full_name)
            except:
                await message.answer(
                    "Возникла ошибка при добавлении вас в базу, попробуйте немного позже, пожалуйста.\nЕсли эта ошибка возникла несколько раз подряд, "
                    "напишите админу @achibtc и скиньте скрин.", reply_markup=duration_subs)
    try:
        price = db.select_price(message.text)
    except sqlite3.Error:
        time.sleep(20)
        price = db.select_price(message.text)

    await message.answer(
        f"Переведите {price[0]} USDT на TRC20 кошелек. После оплаты нажмите кнопку 'Оплатил'",
        reply_markup=payed)
    await message.answer("TCdBe2LZkaP9GWmksDBwCxiJQ1SjoagTbU")


# payed
@dp.message_handler(IsPrivate(), Text(equals=["Оплатил с внешнего кошелька"]))
async def buy_subs(message: types.Message):
    await message.answer(
        "После оплаты транзакции формируется идентификатор транзакции - hash или id транзакции (TxID). "
        "Его можно скопировать из информации об оплате или в истории кошелька.\n"
        "Для проверки оплаты скопируйте сюда, пожалуйста, хеш своей транзакции и отправьте мне сообщением",
        reply_markup=payed)


# payed
@dp.message_handler(IsPrivate(), Text(equals=["Оплатил с Binance"]))
async def buy_subs(message: types.Message):
    await message.answer(
        "После оплаты транзакции формируется идентификатор транзакции - внутренний номер транзакции. "
        "Его можно скопировать из информации об оплате или в истории кошелька.\n"
        "Для проверки оплаты скопируйте сюда, пожалуйста, внутренний номер своей транзакции и отправьте мне сообщением",
        reply_markup=payed)


# payed
@dp.message_handler(IsPrivate(), Text(equals=["Проверить оплату"]))
async def buy_subs(message: types.Message):
    await message.answer("Введите еще раз хеш (id) своей транзакции", reply_markup=payed)


hash_pattern_binance = r"^[0-9]+$"
hash_pattern = r"^[a-zA-Z0-9]+$"


def check_hash(hash_trans):
    full_node = HttpProvider('https://api.trongrid.io')
    solidity_node = HttpProvider('https://api.trongrid.io')
    event_server = HttpProvider('https://api.trongrid.io')
    tron = Tron(full_node=full_node,
                solidity_node=solidity_node,
                event_server=event_server)

    result = tron.trx.get_transaction(hash_trans)
    try:
        trx = tron.fromSun(result.get('raw_data').get('contract')[0].get('parameter').get('value').get('amount'))
    except:
        trx = None
    return result, trx


def convert_to_usdt(trx):
    r = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=TRXUSDT")
    course = r.json()
    return float(trx) * float(course["price"])

# ловим хеш с бинанса
@dp.message_handler(Regexp(hash_pattern_binance))
async def check_payment(message: types.Message):
    await message.answer("Подождите пару минут, сейчас проверю введенные данные")
    client = Client(API_KEY, API_SECRET)
    info = client.get_withdraw_history()
    for result, dic_ in enumerate(info):
        if message.text in dic_.get('txId', ''):
            if not db.select_hash(message.text):
                if dic_.get('status', '') == 1 or dic_.get('status', '') == 6:
                    try:
                        sales = db.select_sales()
                    except sqlite3.Error:
                        time.sleep(20)
                        sales = db.select_sales()
                    now = datetime.datetime.now()
                    # если дата текущая больше даты начала акции и меньше даты окончания акции

                    try:
                        price = db.select_price_to_user(message.from_user.id)
                    except sqlite3.Error:
                        time.sleep(20)
                        price = db.select_price_to_user(message.from_user.id)
                    price_int = price[0]
                    if sales and now >= datetime.datetime(int(sales[0][1].split("-")[0]),
                                                          int(sales[0][1].split("-")[1]),
                                                          int(sales[0][1].split("-")[2])) and now <= datetime.datetime(
                        int(sales[0][2].split("-")[0]),
                        int(sales[0][2].split("-")[1]),
                        int(sales[0][2].split("-")[2])):
                        price_int = price - (100 - {sales[0][0]} / 100)

                    if float(price_int) - 5 <= dic_.get('amount', ''):
                        try:
                            await dp.bot.unban_chat_member(chat_id=GROUP_ID, user_id=message.from_user.id)
                            await dp.bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
                        except:
                            pass
                        kb_subs = await kb_with_link(message.from_user.id)
                        await message.answer("Ваша оплата прошла успешно!", reply_markup=main_keyboard)
                        await message.answer("Вот ваши ссылки для доступа", reply_markup=kb_subs)
                        try:
                            db.add_hash(message.text)  # чтобы потом проверять не повторилась ли транзакция
                        except sqlite3.Error:
                            time.sleep(20)
                            db.add_hash(message.text)

                        try:
                            user = db.select_user(message.from_user.id)
                        except sqlite3.Error:
                            time.sleep(20)
                            user = db.select_user(message.from_user.id)

                        # если есть дата окончания подписки, то надо удалить уведомления, чтобы не писать пользователю зря
                        if user[3]:
                            try:
                                db.delete_alarm_for_users(message.from_user.id)
                            except sqlite3.Error:
                                time.sleep(20)
                                try:
                                    db.delete_alarm_for_users(message.from_user.id)
                                except:
                                    await message.answer(
                                        "Возникла ошибка, попробуйте немного позже, пожалуйста.\nЕсли эта ошибка возникла несколько раз подряд, "
                                        "напишите админу @achibtc и скиньте скрин.", reply_markup=duration_subs)
                        date = ""
                        if user[2]:
                            date_from_db = user[3].split("-")
                            date = datetime.datetime(int(date_from_db[0]), int(date_from_db[1]), int(date_from_db[2]))
                        else:
                            date = datetime.datetime.now()
                        db.edit_user_subs(message.from_user.id, date.strftime("%Y-%m-%d"))
                        await dp.bot.send_message(chat_id=312038680,
                                                  text=f"Добавлен/отредактирован пользователь {message.from_user.id} @{message.from_user.username} {message.from_user.full_name} {message.text}")
                        # записать когда напомнить
                        # user = db.select_user(message.from_user.id)
                        date_end = user[3]
                        date_alarm_week = datetime.datetime.strptime(date_end, "%Y-%m-%d") - relativedelta(days=7)
                        date_alarm_tree_days = datetime.datetime.strptime(date_end, "%Y-%m-%d") - relativedelta(days=3)
                        date_alarm_one_day = datetime.datetime.strptime(date_end, "%Y-%m-%d") - relativedelta(days=1)
                        try:
                            db.add_alarm_for_users(message.from_user.id, date_alarm_week)
                        except sqlite3.Error:
                            time.sleep(20)
                            db.add_alarm_for_users(message.from_user.id, date_alarm_week)

                        try:
                            db.add_alarm_for_users(message.from_user.id, date_alarm_tree_days)
                        except sqlite3.Error:
                            time.sleep(20)
                            db.add_alarm_for_users(message.from_user.id, date_alarm_tree_days)

                        try:
                            db.add_alarm_for_users(message.from_user.id, date_alarm_one_day)
                        except sqlite3.Error:
                            time.sleep(20)
                            db.add_alarm_for_users(message.from_user.id, date_alarm_one_day)
                    else:
                        await message.answer(
                            "Ваш платеж не принят, вы отправили неверную сумму. Свяжитесь с администратором @achibtc, чтобы  разобраться в данной ситуации")
                        await dp.bot.send_message(chat_id=312038680,
                                                  text=f"Мало оплатил пользователь {message.from_user.id} @{message.from_user.username} {message.from_user.full_name} {message.text}")

                elif dic_.get('status', '') == 0:
                    await message.answer("Ваша транзакция не прошла еще, ждем подтверждения операции",
                                         reply_markup=try_payed)
                    await dp.bot.send_message(chat_id=312038680,
                                              text=f"Еще не прошла {message.from_user.id} @{message.from_user.username} {message.from_user.full_name} {message.text}")


            elif db.select_hash(message.text):
                await message.answer(
                        "Данная транзакция уже проверялась и была привязана к другой подписке. Проверьте, пожалуйста, хэш транзакции")
                await dp.bot.send_message(chat_id=312038680,
                                          text=f"Второй раз хеш {message.from_user.id} @{message.from_user.username} {message.from_user.full_name} {message.text} {message.from_user.username}")


        elif message.text not in dic_.get('txId', ''):
            await message.answer(
                    f"Возможно этот платеж предназначен для другого кошелька, "
                    f"проверьте адрес кошелька TCdBe2LZkaP9GWmksDBwCxiJQ1SjoagTbU",
                    reply_markup=try_payed)
            await dp.bot.send_message(chat_id=312038680,
                                text=f"Возможно не тот кошелек {message.from_user.id} @{message.from_user.username} {message.from_user.full_name} {message.text}")


        else:
            await message.answer("Такой транзакции не существует, проверьте еще раз хеш транзакции",
                                    reply_markup=try_payed)
            await dp.bot.send_message(chat_id=312038680,
                                    text=f"Левый хеш {message.from_user.id} @{message.from_user.username} {message.from_user.full_name} {message.text}")
        break

# ловим хеш и проверяем оплату
@dp.message_handler(Regexp(hash_pattern))
async def hash_transaction(message: types.Message):
    # пример hash b6d8106f9e91de59a74f8219aa527cc787e732b25e4d83787bc37acec461bba5
    # кошелек TCdBe2LZkaP9GWmksDBwCxiJQ1SjoagTbU
    # hex кошелька 411d1eebad3bf7fc31695bf514693e613f2f36e83e
    await message.answer("Подождите пару минут, сейчас проверю введенные данные")
    if not db.select_hash(message.text):
        try:
            response = check_hash(message.text)
            if response[0].get("raw_data").get("contract")[0].get("parameter").get("value").get(
                    "contract_address") != None:
                address = response[0].get("raw_data").get("contract")[0].get("parameter").get("value").get(
                    "contract_address")
            else:
                address = response[0].get("raw_data").get("contract")[0].get("parameter").get("value").get("to_address")
            response_status = response[0]['ret'][0]['contractRet']
            if response_status == "SUCCESS" and address == "411d1eebad3bf7fc31695bf514693e613f2f36e83e":
                # try:
                #     await dp.bot.unban_chat_member(chat_id=GROUP_ID, user_id=message.from_user.id)
                #     await dp.bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
                # except:
                #     pass
                # kb_subs = await kb_with_link(message.from_user.id)
                # await message.answer("Ваша оплата прошла успешно!", reply_markup=main_keyboard)
                # await message.answer("Вот ваши ссылки для доступа", reply_markup=kb_subs)
                # try:
                #     db.add_hash(message.text)  # чтобы потом проверять не повторилась ли транзакция
                # except sqlite3.Error:
                #     time.sleep(20)
                #     db.add_hash(message.text)

                # try:
                #     user = db.select_user(message.from_user.id)
                # except sqlite3.Error:
                #     time.sleep(20)
                #     user = db.select_user(message.from_user.id)
                #
                # # если есть дата окончания подписки, то надо удалить уведомления, чтобы не писать пользователю зря
                # if user[3]:
                #     try:
                #         db.delete_alarm_for_users(message.from_user.id)
                #     except sqlite3.Error:
                #         time.sleep(20)
                #         try:
                #             db.delete_alarm_for_users(message.from_user.id)
                #         except:
                #             await message.answer(
                #                 "Возникла ошибка, попробуйте немного позже, пожалуйста.\nЕсли эта ошибка возникла несколько раз подряд, "
                #                 "напишите админу @achibtc и скиньте скрин.", reply_markup=duration_subs)
                # date = ""
                # if user[2]:
                #     date_from_db = user[3].split("-")
                #     date = datetime.datetime(int(date_from_db[0]), int(date_from_db[1]), int(date_from_db[2]))
                # else:
                #     date = datetime.datetime.now()
                # try:
                #     db.edit_user_subs(message.from_user.id, date.strftime("%Y-%m-%d"))
                # except sqlite3.Error:
                #     time.sleep(20)
                #     db.edit_user_subs(message.from_user.id, date.strftime("%Y-%m-%d"))
                #
                # # записать когда напомнить
                # # try:
                # #     user = db.select_user(message.from_user.id)
                # # except sqlite3.Error:
                # #     time.sleep(20)
                # #     user = db.select_user(message.from_user.id)
                #
                # date_end = user[3]
                # date_alarm_week = datetime.datetime.strptime(date_end, "%Y-%m-%d") - relativedelta(days=7)
                # date_alarm_tree_days = datetime.datetime.strptime(date_end, "%Y-%m-%d") - relativedelta(days=3)
                # date_alarm_one_day = datetime.datetime.strptime(date_end, "%Y-%m-%d") - relativedelta(days=1)
                #
                # try:
                #     db.add_alarm_for_users(message.from_user.id, date_alarm_week)
                # except sqlite3.Error:
                #     time.sleep(20)
                #     db.add_alarm_for_users(message.from_user.id, date_alarm_week)
                #
                # try:
                #     db.add_alarm_for_users(message.from_user.id, date_alarm_tree_days)
                # except sqlite3.Error:
                #     time.sleep(20)
                #     db.add_alarm_for_users(message.from_user.id, date_alarm_tree_days)
                #
                # try:
                #     db.add_alarm_for_users(message.from_user.id, date_alarm_one_day)
                # except sqlite3.Error:
                #     time.sleep(20)
                #     db.add_alarm_for_users(message.from_user.id, date_alarm_one_day)


                try:
                    sales = db.select_sales()
                except sqlite3.Error:
                    time.sleep(20)
                    sales = db.select_sales()
                now = datetime.datetime.now()
                # если дата текущая больше даты начала акции и меньше даты окончания акции
                usdt = convert_to_usdt(response[1])
                try:
                    price = db.select_price_to_user(message.from_user.id)
                except sqlite3.Error:
                    time.sleep(20)
                    price = db.select_price_to_user(message.from_user.id)
                price_int = price[0]
                if sales and now >= datetime.datetime(int(sales[0][1].split("-")[0]), int(sales[0][1].split("-")[1]),
                                                      int(sales[0][1].split("-")[2])) and now <= datetime.datetime(
                    int(sales[0][2].split("-")[0]),
                    int(sales[0][2].split("-")[1]),
                    int(sales[0][2].split("-")[2])):
                    price_int = price - (100 - {sales[0][0]} / 100)

                if float(price_int) - 5 <= usdt:
                    try:
                        await dp.bot.unban_chat_member(chat_id=GROUP_ID, user_id=message.from_user.id)
                        await dp.bot.unban_chat_member(chat_id=CHANNEL_ID, user_id=message.from_user.id)
                    except:
                        pass
                    kb_subs = await kb_with_link(message.from_user.id)
                    await message.answer("Ваша оплата прошла успешно!", reply_markup=main_keyboard)
                    await message.answer("Вот ваши ссылки для доступа", reply_markup=kb_subs)
                    try:
                        db.add_hash(message.text)  # чтобы потом проверять не повторилась ли транзакция
                    except sqlite3.Error:
                        time.sleep(20)
                        db.add_hash(message.text)

                    try:
                        user = db.select_user(message.from_user.id)
                    except sqlite3.Error:
                        time.sleep(20)
                        user = db.select_user(message.from_user.id)

                    # если есть дата окончания подписки, то надо удалить уведомления, чтобы не писать пользователю зря
                    if user[3]:
                        try:
                            db.delete_alarm_for_users(message.from_user.id)
                        except sqlite3.Error:
                            time.sleep(20)
                            try:
                                db.delete_alarm_for_users(message.from_user.id)
                            except:
                                await message.answer(
                                    "Возникла ошибка, попробуйте немного позже, пожалуйста.\nЕсли эта ошибка возникла несколько раз подряд, "
                                    "напишите админу @achibtc и скиньте скрин.", reply_markup=duration_subs)
                    date = ""
                    if user[2]:
                        date_from_db = user[3].split("-")
                        date = datetime.datetime(int(date_from_db[0]), int(date_from_db[1]), int(date_from_db[2]))
                    else:
                        date = datetime.datetime.now()
                    db.edit_user_subs(message.from_user.id, date.strftime("%Y-%m-%d"))
                    await dp.bot.send_message(chat_id=312038680, text=f"Добавлен/отредактирован пользователь {message.from_user.id} @{message.from_user.username} {message.from_user.full_name} {message.text}")
                    # записать когда напомнить
                    # user = db.select_user(message.from_user.id)
                    date_end = user[3]
                    date_alarm_week = datetime.datetime.strptime(date_end, "%Y-%m-%d") - relativedelta(days=7)
                    date_alarm_tree_days = datetime.datetime.strptime(date_end, "%Y-%m-%d") - relativedelta(days=3)
                    date_alarm_one_day = datetime.datetime.strptime(date_end, "%Y-%m-%d") - relativedelta(days=1)
                    try:
                        db.add_alarm_for_users(message.from_user.id, date_alarm_week)
                    except sqlite3.Error:
                        time.sleep(20)
                        db.add_alarm_for_users(message.from_user.id, date_alarm_week)

                    try:
                        db.add_alarm_for_users(message.from_user.id, date_alarm_tree_days)
                    except sqlite3.Error:
                        time.sleep(20)
                        db.add_alarm_for_users(message.from_user.id, date_alarm_tree_days)

                    try:
                        db.add_alarm_for_users(message.from_user.id, date_alarm_one_day)
                    except sqlite3.Error:
                        time.sleep(20)
                        db.add_alarm_for_users(message.from_user.id, date_alarm_one_day)
                else:
                    await message.answer(
                        "Ваш платеж не принят, вы отправили неверную сумму. Свяжитесь с администратором @achibtc, чтобы  разобраться в данной ситуации")
                    await dp.bot.send_message(chat_id=312038680,
                                        text=f"Мало оплатил пользователь {message.from_user.id} @{message.from_user.username} {message.from_user.full_name} {message.text}")


            elif response_status == "SUCCESS" and address != "411d1eebad3bf7fc31695bf514693e613f2f36e83e":
                await message.answer(
                    f"Этот платеж предназначен для другого кошелька, "
                    f"отправьте платеж на кошелек TCdBe2LZkaP9GWmksDBwCxiJQ1SjoagTbU",
                    reply_markup=try_payed)
                await dp.bot.send_message(chat_id=312038680,
                                          text=f"Не тот кошелек {message.from_user.id} @{message.from_user.username} {message.from_user.full_name} {message.text}")

            else:
                await message.answer("Ваша транзакция не прошла еще, ждем подтверждения операции",
                                     reply_markup=try_payed)
                await dp.bot.send_message(chat_id=312038680,
                                          text=f"Еще не прошла {message.from_user.id} @{message.from_user.username} {message.from_user.full_name} {message.text}")

        except ValueError:
            await message.answer("Такой транзакции не существует, проверьте еще раз хеш транзакции",
                                 reply_markup=try_payed)
            await dp.bot.send_message(chat_id=312038680,
                                      text=f"Левый хеш {message.from_user.id} @{message.from_user.username} {message.from_user.full_name} {message.text}")
    else:
        await message.answer(
            "Данная транзакция уже проверялась и была привязана к другой подписке. Проверьте, пожалуйста, хэш транзакции")
        await dp.bot.send_message(chat_id=312038680,
                                  text=f"Второй раз хеш {message.from_user.id} @{message.from_user.username} {message.from_user.full_name} {message.text} {message.from_user.username}")


# buy_with_sale_and_back
@dp.message_handler(IsPrivate(), Text(equals=["Оплатить со скидкой"]))
async def buy_subs(message: types.Message):
    await message.answer("Выберите вариант подписки", reply_markup=duration_subs_sale)
