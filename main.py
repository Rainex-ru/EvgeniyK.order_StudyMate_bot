import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import load_config
from bot import register_handlers
from database.models import init_db

async def main():
    # 1. Логирование
    logging.basicConfig(level=logging.INFO)

    # 2. Конфигурация и объекты бота
    config = load_config()
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

    # 3. Инициализация БД и регистрация хендлеров
    init_db()
    register_handlers(dp)

    # 4. Запуск поллинга
    try:
        await dp.start_polling(bot)
    finally:
        # 5. Грейсфул-шаутдаун: закрыть сессию бота
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())