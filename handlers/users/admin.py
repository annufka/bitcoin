import datetime

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import CallbackQuery

from filters.type_chat import IsPrivate
from keyboards.inline.inline import kb_with_sales, kb_months
from loader import dp, db
from states.admin_state import EnterPrice, EnterSale


# Сменить стоимость за {}
@dp.message_handler(IsPrivate(), Text(equals=["Сменить стоимость подписки"]), state=None)
async def edit_price(message: types.Message):
    months = await kb_months()
    await message.answer("Выберите тип подписки", reply_markup=months)
    await EnterPrice.duration.set()


@dp.callback_query_handler(IsPrivate(), Text(contains="month#"), state=EnterPrice.duration)
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
    db.edit_price(data["duration"], data["enter_price"])
    await message.answer("Записал")
    await state.finish()


# Включить пробные две недели для всех пользователей
@dp.message_handler(IsPrivate(), Text(equals=["Включить пробные две недели для всех пользователей"]))
async def edit_price(message: types.Message):
    # tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)

    # для теста
    tomorrow = datetime.datetime.now()

    db.treal_on(tomorrow.strftime("%Y-%m-%d"))
    await message.answer("Пробная подписка для всех пользователей будет включена завтра")


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
    db.add_sale(data["enter_sale"], data["enter_begin"], data["enter_end"], data["enter_text"])
    await message.answer("Записал данные акции")
    await state.finish()


# Удалить акцию
@dp.message_handler(IsPrivate(), Text(equals=["Удалить акцию"]))
async def delete_sale(message: types.Message):
    sales = await kb_with_sales()
    await message.answer("Выберите акцию, которую хотите удалить\n\n", reply_markup=sales)


@dp.callback_query_handler(IsPrivate(), Text(contains="del#"))
async def delete_from_db_sale(call: CallbackQuery):
    await call.answer()
    date = (call.data.split("#")[1]).split("-")
    date_date = datetime.date(int(date[0]), int(date[1]), int(date[2]))
    db.delete_sale(date_date)
    await call.message.edit_text(text="Вы удалили акцию", reply_markup=None)
