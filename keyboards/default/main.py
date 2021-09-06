from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Моя подписка")
        ],
        [
            KeyboardButton(text="Тарифы")
        ],
        [
            KeyboardButton(text="Акции")
        ],
    ],
    resize_keyboard=True
)

price_and_back = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Тарифы")
        ],
        [
            KeyboardButton(text="Назад")
        ],
    ],
    resize_keyboard=True
)

extend_and_back = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Продлить подписку")
        ],
        [
            KeyboardButton(text="Назад")
        ],
    ],
    resize_keyboard=True
)

buy_and_back = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Оплатить")
        ],
        [
            KeyboardButton(text="Назад")
        ],
    ],
    resize_keyboard=True
)

back = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Назад")
        ],
    ],
    resize_keyboard=True
)

treal_free = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Вступить в VIP")
        ],
        [
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True
)

duration_subs = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="1 месяц")
        ],
        [
            KeyboardButton(text="4 месяца")
        ],
        [
            KeyboardButton(text="6 месяцев")
        ],
        [
            KeyboardButton(text="1 год")
        ],
        [
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True
)

payed = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Оплатил")
        ],
        [
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True
)

try_payed = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Проверить оплату")
        ],
        [
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True
)

admins_main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Сменить стоимость подписки")
        ],
        [
            KeyboardButton(text="Включить пробные две недели для всех пользователей")
        ],
        [
            KeyboardButton(text="Добавить акцию")
        ],
        [
            KeyboardButton(text="Удалить акцию")
        ],

    ],
    resize_keyboard=True
)

buy_with_sale_and_back = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Оплатить со скидкой")
        ],
        [
            KeyboardButton(text="Назад")
        ],
    ],
    resize_keyboard=True
)


duration_subs_sale = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="1 месяц со скидкой")
        ],
        [
            KeyboardButton(text="4 месяца со скидкой")
        ],
        [
            KeyboardButton(text="6 месяцев со скидкой")
        ],
        [
            KeyboardButton(text="1 год со скидкой")
        ],
        [
            KeyboardButton(text="Назад")
        ]
    ],
    resize_keyboard=True
)
