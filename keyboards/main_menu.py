from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ================== دیکشنری ایموجی‌های پرمیوم ==================
PREMIUM = {
    "shop": "6084478403564541578",       # 🛒 خرید
    "test": "4981274701641812058",       # ✅ اکانت تست
    "wallet": "4981354978875541290",     # 🌟 کیف پول
    "account": "4981188033496745757",    # 🐹 حساب کاربری
    "support": "4981420305328113641",    # 🌀 پشتیبانی
    "rules": "6086975703708866199",      # 👀 قوانین
    "admin": "4985741377435337443",      # 🤎 ادمین
    "back": "6087055285157893604",       # 📤 برگشت
    "cancel": "5771395074600472173",     # 💀 انصراف
    "referral": "5400254220270055279",   # 🔗 لینک دعوت
}

def get_main_menu(is_admin=False):
    """کیبورد اصلی منو (ریپلای) با ایموجی پرمیوم و دکمه‌های رنگی"""

    buttons = [
        [
            KeyboardButton(
                text="🛒 خرید حجم",
                style="primary",  # 🔵 آبی - اقدام اصلی
                icon_custom_emoji_id=PREMIUM["shop"]
            )
        ],
        [
            KeyboardButton(
                text="🎰 گردونه شانس",
                style="success",  # 🟢 سبز - موفقیت
                icon_custom_emoji_id=PREMIUM["test"]
            ),
            KeyboardButton(
                text="💳 کیف پول",
                style="success",  # 🟢 سبز - مالی
                icon_custom_emoji_id=PREMIUM["wallet"]
            )
        ],
        [
            KeyboardButton(
                text="👤 حساب کاربری",
                style="primary",  # 🔵 آبی - اطلاعات
                icon_custom_emoji_id=PREMIUM["account"]
            ),
            KeyboardButton(
                text="💬 پشتیبانی",
                style="success",  # 🟢 سبز - پشتیبانی
                icon_custom_emoji_id=PREMIUM["support"]
            )
        ],
        [
            KeyboardButton(
                text="📜 قوانین و مقررات",
                style="danger",  # 🔴 قرمز - هشدار/قوانین
                icon_custom_emoji_id=PREMIUM["rules"]
            )
        ],
        [
            KeyboardButton(
                text="🔗 لینک دعوت",
                style="primary",  # 🔵 آبی - دعوت دوستان
                icon_custom_emoji_id=PREMIUM["referral"]
            )
        ]
    ]

    if is_admin:
        buttons.append([
            KeyboardButton(
                text="👑 پنل ادمین",
                style="danger",  # 🔴 قرمز - دسترسی ویژه
                icon_custom_emoji_id=PREMIUM["admin"]
            )
        ])

    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="از منوی زیر انتخاب کن... 🎯"
    )


def get_back_button():
    """دکمه بازگشت"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🔙 بازگشت",
                    style="danger",
                    icon_custom_emoji_id=PREMIUM["back"]
                )
            ]
        ],
        resize_keyboard=True
    )


def get_cancel_button():
    """دکمه انصراف"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="❌ انصراف",
                    style="danger",
                    icon_custom_emoji_id=PREMIUM["cancel"]
                )
            ]
        ],
        resize_keyboard=True
    )
