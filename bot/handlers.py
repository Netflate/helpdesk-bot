from aiogram import Router, types
from aiogram.filters import CommandStart
from utils.localization import localization
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
router = Router()

@router.message(CommandStart())
async def start_command(msg: types.Message):
    buttons = []
    i = 1
    while True:
        choice = localization.get(f"choice{i}", localization.lang)
        print(choice)
        print(type(choice))
        if choice is None:  # если ключ не найден - выходим
            break
        buttons.append([InlineKeyboardButton(text=choice, callback_data=f"choice{i}")])
        i += 1
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await msg.answer(
        localization.get("start_message", localization.lang),
        reply_markup=keyboard
    )

