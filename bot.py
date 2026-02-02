from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
    
)
import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import sqlite3

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MASTER_CHAT_ID = int(os.getenv("MASTER_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==== БАЗА ДАННЫХ ====
DB_PATH = "bot.db"

def get_db():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        owner_id INTEGER,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id INTEGER,
        user_id INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id INTEGER,
        client_user_id INTEGER,
        client_name TEXT,
        phone TEXT,
        brand TEXT,
        model TEXT,
        plate TEXT,
        service_type TEXT,
        urgency TEXT,
        comment TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

# ===== СЛОВАРИ =====
SERVICE_NAMES = {
    "diagnostic": "Диагностика",
    "oil-change": "Замена масла",
    "tires": "Шины и диски",
    "brake": "Тормозная система",
    "engine": "Ремонт двигателя",
    "transmission": "Коробка передач",
    "suspension": "Подвеска",
    "body": "Кузовные работы",
    "other": "Другое"
}

URGENCY_NAMES = {
    "low": "Обычный (7+ дней)",
    "medium": "Средний (3-5 дней)",
    "high": "Срочный (1-2 дня)",
    "urgent": "Очень срочный (сегодня)"
}

STATUS_LABELS = {
    "accepted": "✅ Принято",
    "called": "📞 Связались",
    "rejected": "❌ Отказ"
}


# ===== КНОПКИ АДМИНКИ =====
def admin_keyboard(request_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принято", callback_data=f"status:accepted:{request_id}"),
            InlineKeyboardButton(text="📞 Связались", callback_data=f"status:called:{request_id}")
        ],
        [
            InlineKeyboardButton(text="❌ Отказ", callback_data=f"status:rejected:{request_id}")
        ]
    ])

# ===== /start =====
@dp.message(F.text == "/start")
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="🚗 Записаться в автосервис",
                web_app=WebAppInfo(url="https://tatr0.github.io/bot_telegram/")
                
            )
        ]],
        resize_keyboard=True
    )
    await message.answer("Запишитесь в автосервис онлайн 👇", reply_markup=keyboard)

# ===== ПРИЁМ ЗАЯВКИ =====
@dp.message(F.web_app_data)
async def webapp_handler(message: Message):
    try:
        data = json.loads(message.web_app_data.data)

        # === ВСЕ ПЕРЕМЕННЫЕ СРАЗУ ===
        name = (data.get("client_name") or "").strip() or "Не указано"
        phone = (data.get("phone") or "").strip() or "—"

        brand = data.get("brand", "—")
        model = data.get("model", "—")
        plate = data.get("plate", "—")
        service_key = data.get("service")
        urgency_key = data.get("urgency")
        comment = data.get("comment", "")

        service_name = SERVICE_NAMES.get(service_key, service_key or "—")
        urgency_name = URGENCY_NAMES.get(urgency_key, urgency_key or "—")

        # === СОХРАНЕНИЕ В БД ===
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO requests (
                service_id,
                client_user_id,
                client_name,
                phone,
                brand,
                model,
                plate,
                service_type,
                urgency,
                comment,
                status,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1,
            message.from_user.id,
            name,
            phone,
            brand,
            model,
            plate,
            service_key,
            urgency_key,
            comment,
            "new",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        request_id = cur.lastrowid
        conn.commit()
        conn.close()

        # === СООБЩЕНИЕ АДМИНУ ===
        admin_message = (
            "<b>═══ 🚗 НОВАЯ ЗАЯВКА ═══</b>\n\n"
            "<b>👤 КЛИЕНТ</b>\n"
            f"Имя: <b>{name}</b>\n"
            f"Телефон: <code>+{phone}</code>\n\n"
            "<b>🚙 АВТО</b>\n"
            f"Марка: {brand}\n"
            f"Модель: {model}\n"
            f"Гос номер: <code>{plate}</code>\n\n"
            "<b>🔧 УСЛУГА</b>\n"
            f"Тип: {service_name}\n"
            f"Срочность: {urgency_name}\n\n"
            f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        if comment:
            admin_message += f"\n\n<b>💬 Комментарий</b>\n{comment}"

        await bot.send_message(
            MASTER_CHAT_ID,
            admin_message,
            parse_mode="HTML",
            reply_markup=admin_keyboard(str(request_id))
        )

        await message.answer(
            "✅ <b>Заявка отправлена!</b>\n\nМы скоро с вами свяжемся 📞",
            parse_mode="HTML"
        )

    except Exception as e:
        print("WEBAPP ERROR:", e)
        await message.answer("❌ Ошибка при отправке заявки")




# ===== FALLBACK =====
@dp.message()
async def fallback(message: Message):
    await message.answer(
        "Нажмите кнопку ниже 👇",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[
                KeyboardButton(
                    text="🚗 Записаться в автосервис",
                    web_app=WebAppInfo(url="https://tatr0.github.io/bot_telegram/")
                )
            ]],
            resize_keyboard=True
        )
    )
#==== ПРОВЕРКА БАЗЫ ======
@dp.message(F.text == "/debug_db")
async def debug_db(message: Message):
    if message.from_user.id != MASTER_CHAT_ID:
        return

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, client_name, phone, brand, model, service_type, urgency, status, created_at
        FROM requests
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cur.fetchone()
    conn.close()

    if not row:
        await message.answer("База пустая")
        return

    (
        req_id, name, phone, brand, model,
        service, urgency, status, created_at
    ) = row

    text = (
        "<b>🧪 Последняя заявка</b>\n\n"
        f"ID: {req_id}\n"
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Марка: {brand}\n"
        f"Модель: {model}\n"
        f"Услуга: {SERVICE_NAMES.get(service, service)}\n"
        f"Срочность: {URGENCY_NAMES.get(urgency, urgency)}\n"
        f"Статус: {status}\n"
        f"Создано: {created_at}"
    )

    await message.answer(text, parse_mode="HTML")

# ===== MAIN =====
async def main():
    init_db()
    print("✅ База данных инициализирована")
    print("✅ Бот с админкой запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
