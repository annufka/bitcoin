from aiogram.dispatcher.filters.state import StatesGroup, State


class EnterPrice(StatesGroup):
    duration = State()
    enter_price = State()


class EnterSale(StatesGroup):
    enter_sale = State()
    enter_begin = State()
    enter_end = State()
    enter_text = State()
