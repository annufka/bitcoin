import asyncio

from aiogram import executor
from aiogram.utils.executor import start_webhook

from data.config import WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT
from loader import db, SSL_CERTIFICATE, ssl_context, bot
import middlewares, filters, handlers
from schedule_delete_sale import deleteSale, deleteTreal
from schedule_user import startTimer, kick_user
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands

loop = asyncio.get_event_loop()

async def on_startup(dispatcher):

    # webhooks
    try:
        webhook = await bot.get_webhook_info()

        # If URL is bad
        if webhook.url != WEBHOOK_URL:
            # If URL doesnt match current - remove webhook
            if not webhook.url:
                await bot.delete_webhook()

    except:
        pass
    await bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=SSL_CERTIFICATE
    )

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
    # await on_startup_notify(dispatcher)


if __name__ == '__main__':
    from handlers import dp

    loop = asyncio.get_event_loop()
    loop.create_task(startTimer(86400))
    loop.create_task(deleteSale(43200))
    loop.create_task(deleteTreal(43200))
    loop.create_task(kick_user(43200))
    # loop.create_task(startTimer(86400))
    # loop.create_task(deleteSale(86400))
    # loop.create_task(deleteTreal(86400))
    # loop.create_task(kick_user(86400))


    start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            loop=loop,
            on_startup=on_startup,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
            ssl_context=ssl_context
        )
    # executor.start_polling(dp, on_startup=on_startup)
