import os
from dotenv import load_dotenv

load_dotenv()

# ===== BOT CONFIGURATION =====
BOT_TOKEN = os.getenv("BOT_TOKEN")
MASTER_CHAT_ID = int(os.getenv("MASTER_CHAT_ID"))

# ===== SERVICE NAMES =====
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

# ===== URGENCY NAMES =====
URGENCY_NAMES = {
    "low": "Обычный (7+ дней)",
    "medium": "Средний (3-5 дней)",
    "high": "Срочный (1-2 дня)",
    "urgent": "Очень срочный (сегодня)"
}

# ===== STATUS LABELS =====
STATUS_LABELS = {
    "accepted": "✅ Принято",
    "called": "📞 Связались",
    "rejected": "❌ Отказ"
}