import asyncio
import logging
from utils.db_api.create_user import init_db # init_db ni import qilasiz
from loader import bot, dp
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup():
    await set_default_commands(bot)
    await on_startup_notify(bot)


async def main():
    await init_db()
    logging.basicConfig(level=logging.INFO)
    middlewares.setup(dp)
    filters.setup(dp)
    handlers.setup(dp)

    await on_startup()
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
