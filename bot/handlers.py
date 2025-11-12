from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start_command(msg: types.Message):
    await msg.answer("Привет! Я бот поддержки 😊")
