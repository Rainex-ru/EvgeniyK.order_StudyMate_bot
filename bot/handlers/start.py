from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("start"))
async def cmd_start(message:Message):
    await message.answer("Привет! Я StudyMate - твой помощник в школьной жизни!")
    await message.answer("Я помогу тебе с расписанием, домашними заданиями и многим другим. Просто напиши мне, что ты хочешь сделать!")