from aiogram import Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database.db import get_db
from datetime import datetime

# ===== STATES =====
class RegisterService(StatesGroup):
    waiting_name = State()
    waiting_number = State()
    waiting_admin_id = State()

# ===== REGISTER SERVICE HANDLER =====
async def register_service(message: Message, state: FSMContext):
    await state.set_state(RegisterService.waiting_name)
    await message.answer("🏷 Введите название автосервиса:")

# ===== SAVE SERVICE NAME =====
async def save_service_name(message: Message, state: FSMContext):
    service_name = message.text.strip()
    
    if not service_name:
        await message.answer("❌ Название не может быть пустым. Попробуйте снова:")
        return

    await state.update_data(service_name=service_name)
    await state.set_state(RegisterService.waiting_number)
    await message.answer("📞 Введите номер телефона сервиса:")

# ===== SAVE SERVICE NUMBER =====
async def save_service_number(message: Message, state: FSMContext):
    service_number = message.text.strip()
    
    if not service_number:
        await message.answer("❌ Номер не может быть пустым. Попробуйте снова:")
        return

    await state.update_data(service_number=service_number)
    await state.set_state(RegisterService.waiting_admin_id)
    await message.answer("🆔 Введите Telegram ID администратора:")

# ===== SAVE ADMIN ID =====
async def save_admin_id(message: Message, state: FSMContext):
    try:
        admin_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ ID должен быть числом. Попробуйте снова:")
        return

    data = await state.get_data()
    service_name = data.get("service_name")
    service_number = data.get("service_number")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO services (name, number, owner_id, created_at) VALUES (?, ?, ?, ?)",
        (
            service_name,
            service_number,
            message.from_user.id,
            datetime.now().isoformat()
        )
    )

    service_id = cur.lastrowid

    cur.execute(
        "INSERT INTO admins (service_id, user_id) VALUES (?, ?)",
        (service_id, admin_id)
    )

    conn.commit()
    conn.close()

    await state.clear()

    await message.answer(
        "✅ <b>Автосервис зарегистрирован!</b>\n\n"
        f"🏷 Название: <b>{service_name}</b>\n"
        f"📞 Номер: <code>{service_number}</code>\n"
        f"🆔 Service ID: <code>{service_id}</code>\n"
        f"👨‍💼 Администратор ID: <code>{admin_id}</code>\n\n"
        "ℹ️ Сохраните эти данные — они понадобятся для управления заявками",
        parse_mode="HTML"
    )

# ===== REGISTER HANDLERS =====
def register_service_handlers(dp: Dispatcher):
    dp.message.register(register_service, F.text == "/register_service")
    dp.message.register(save_service_name, RegisterService.waiting_name)
    dp.message.register(save_service_number, RegisterService.waiting_number)
    dp.message.register(save_admin_id, RegisterService.waiting_admin_id)