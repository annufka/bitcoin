from aiogram import executor

from loader import dp, db
import middlewares, filters, handlers
from schedule_user import scheduler
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)

    db.create_table_subs()
    db.create_table_users()
    db.create_table_free_treal()
    db.create_table_link_to_subs()
    db.create_table_sale()
    db.create_table_used_hash()
    db.create_schedule()

    # Уведомляет про запуск
    await on_startup_notify(dispatcher)
    await scheduler()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
