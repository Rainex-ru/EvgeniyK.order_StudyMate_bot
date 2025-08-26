import asyncio
from aiogram import Bot, Dispatcher
from config import load_config
from bot import register_handlers
from database.models import init_db
import logging

config = load_config()
bot = Bot(token=config.bot_token)
dp = Dispatcher()

register_handlers(dp)
init_db()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
