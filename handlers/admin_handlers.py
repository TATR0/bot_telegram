from aiogram import Dispatcher, F
from aiogram.types import Message
from keyboards.keyboards import start_keyboard, fallback_keyboard

# ===== START HANDLER =====
async def start(message: Message):
    await message.answer(
        "Запишитесь в автосервис онлайн 👇",
        reply_markup=start_keyboard()
    )

# ===== FALLBACK HANDLER =====
async def fallback(message: Message):
    await message.answer(
        "Нажмите кнопку ниже 👇",
        reply_markup=fallback_keyboard()
    )

# ===== REGISTER HANDLERS =====
def register_admin_handlers(dp: Dispatcher):
    dp.message.register(start, F.text == "/start")
    dp.message.register(fallback, ~F.text.startswith("/"))