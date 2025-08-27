from aiogram import Dispatcher
from bot.handlers import students, start, admin

def register_handlers(dp: Dispatcher):
    dp.include_router(start.router)
    dp.include_router(students.router)
    dp.include_router(admin.router)

