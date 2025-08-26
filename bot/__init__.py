from aiogram import Dispatcher
from bot.handlers import start

def register_handlers(dp: Dispatcher):
    dp.include_router(start.router)
