from aiogram import Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import json
from datetime import datetime
from config import SERVICE_NAMES, URGENCY_NAMES, MASTER_CHAT_ID, BOT_TOKEN
from database.db import get_db
from keyboards.keyboards import admin_keyboard
from aiogram import Bot

bot = Bot(token=BOT_TOKEN)

# ===== WEBAPP HANDLER =====
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
            datetime.now().strftime("%Y-%m-%d %H:%M")
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

# ===== REGISTER HANDLERS =====
def register_request_handlers(dp: Dispatcher):
    dp.message.register(webapp_handler, F.web_app_data)