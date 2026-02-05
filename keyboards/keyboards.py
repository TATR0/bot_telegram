from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

# ===== ADMIN KEYBOARD =====
def admin_keyboard(request_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принято", callback_data=f"status:accepted:{request_id}")            
        ],
        [
            InlineKeyboardButton(text="📞 Связались", callback_data=f"status:called:{request_id}")
        ],
        [
            InlineKeyboardButton(text="❌ Отказ", callback_data=f"status:rejected:{request_id}")
        ]
    ])

# ===== START KEYBOARD =====
def start_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="🚗 Записаться в автосервис",
                web_app=WebAppInfo(url="https://tatr0.github.io/bot_telegram/")
            )
        ]],
        resize_keyboard=True
    )

# ===== FALLBACK KEYBOARD =====
def fallback_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(
                text="🚗 Записаться в автосервис",
                web_app=WebAppInfo(
                    url="https://tatr0.github.io/bot_telegram/"
                )
            )
        ]],
        resize_keyboard=True
    )