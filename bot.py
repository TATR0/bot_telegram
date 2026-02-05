from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
import asyncio
import os
from dotenv import load_dotenv

from config import BOT_TOKEN
from database.db import init_db
from handlers import (
    register_service_handlers,
    register_request_handlers,
    register_admin_handlers
)

load_dotenv()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===== REGISTER ALL HANDLERS =====
register_service_handlers(dp)
register_request_handlers(dp)
register_admin_handlers(dp)

# ===== SET BOT COMMANDS =====
async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="register_service", description="Подключить автосервис"),
        BotCommand(command="add_admin", description="Добавить администратора"),
        BotCommand(command="requests", description="История заявок"),       
    ]
    await bot.set_my_commands(commands)

# ===== MAIN =====
async def main():
    init_db()
    print("✅ База данных инициализирована")
    print("✅ Бот с админкой запущен")
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())