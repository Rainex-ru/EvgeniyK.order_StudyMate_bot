from aiogram import Dispatcher
from bot.handlers import start, students

def register_handlers(dp: Dispatcher):
    dp.include_router(start.router)
    dp.include_router(students.router)
