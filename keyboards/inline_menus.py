from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================== دیکشنری ایموجی‌های پرمیوم ==================
PREMIUM = {
    "wallet": "4967518033061872209",
    "money": "5033080906403808074",
    "alert": "4990219185784095465",
    "coin_tether": "5949395935439099112",
    "coin_tron": "5949382251673292713",
    "cash": "6084573665939166516",
    "diamond": "6084795634143990713",
    "loading": "6084846396362462760",
    "success": "6298804341151107148",
    "danger": "5771395074600472173",
    "back": "6087055285157893604",
    "support": "5971889748615105853",
    "star": "5978776771623914876",
    "energy": "6084367318530397918",
    "chart": "6084890063294959714",
    "lock": "5400250874490532265",
    "unlock": "6298804341151107148",
    "history": "6084890063294959714",
    "gift": "4985741377435337443",
    "user": "6219810752887262728",
    "send": "6087055285157893604",
    "info": "6087054662387635231",
    "percent": "6086889112873210296",
    "earth": "5397798946380721942",
    "fire": "5400233320959191625",
    "winner": "4985741377435337443",
    "dragon": "6084723220995381369",
    "premium_star": "5978776771623914876",
    "mouse_click": "5400286088927392515",
    "flying_money": "5399868497847135951",
    "exclamation": "6084463229445085650",
    "chain": "6084478403564541578",
    "time": "5971895340662526314",
    "top": "6084890063294959714",
    "edit": "6086723567653753735",
    "spray": "4981418681830475148",
    "dollar_sign": "5400247352617349412",
    "admin": "6084723220995381369",
    "orders": "4970023558068568720",
    "shield": "5033242607627535090",
    "flag": "4969862428075491925",
    "shopping": "5033300671290409647",
    "server": "6084478403564541578",
    "slot": "5400585043394618397"  # <-- اضافه شد
}

# ============================================================
# ========== دکمه‌های سرور ==========
# ============================================================
def get_server_buttons():
    from models import Product
    products = Product.get_all()
    
    buttons = []
    row = []
    
    for product in products:
        if product["is_active"]:
            row.append(InlineKeyboardButton(
                text=product['name'],
                callback_data=f"server_{product['id']}",
                style=product["button_color"],
                icon_custom_emoji_id=PREMIUM["earth"]
            ))
    
    for i in range(0, len(row), 2):
        buttons.append(row[i:i+2])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های مدت زمان ==========
# ============================================================
def get_duration_buttons():
    buttons = [
        [
            InlineKeyboardButton(
                text="۳۰ روزه +۲۰,۰۰۰ تومان",
                callback_data="duration_30",
                style="danger",
                icon_custom_emoji_id=PREMIUM["time"]
            )
        ],
        [
            InlineKeyboardButton(
                text="۶۰ روزه +۳۰,۰۰۰ تومان",
                callback_data="duration_60",
                style="primary",
                icon_custom_emoji_id=PREMIUM["time"]
            )
        ],
        [
            InlineKeyboardButton(
                text="۹۰ روزه +۵۰,۰۰۰ تومان",
                callback_data="duration_90",
                style="success",
                icon_custom_emoji_id=PREMIUM["time"]
            )
        ],
        [
            InlineKeyboardButton(
                text="بازگشت به مرحله قبل",
                callback_data="back_to_server",
                style="primary",
                icon_custom_emoji_id=PREMIUM["back"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های تعداد کاربر ==========
# ============================================================
def get_user_count_buttons():
    buttons = [
        [
            InlineKeyboardButton(
                text="تک کاربره +۱۰,۰۰۰ تومان",
                callback_data="usercount_1",
                style="primary",
                icon_custom_emoji_id=PREMIUM["user"]
            )
        ],
        [
            InlineKeyboardButton(
                text="دو کاربره +۲۰,۰۰۰ تومان",
                callback_data="usercount_2",
                style="danger",
                icon_custom_emoji_id=PREMIUM["user"]
            )
        ],
        [
            InlineKeyboardButton(
                text="سه کاربره +۳۰,۰۰۰ تومان",
                callback_data="usercount_3",
                style="success",
                icon_custom_emoji_id=PREMIUM["user"]
            )
        ],
        [
            InlineKeyboardButton(
                text="بازگشت به مرحله قبل",
                callback_data="back_to_duration",
                style="primary",
                icon_custom_emoji_id=PREMIUM["back"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های پرداخت نهایی ==========
# ============================================================
def get_final_payment_button():
    buttons = [
        [InlineKeyboardButton(
            text="پرداخت نهایی و تایید خرید",
            callback_data="final_payment",
            style="success",
            icon_custom_emoji_id=PREMIUM["success"]
        )],
        [InlineKeyboardButton(
            text="بازگشت به مرحله قبل",
            callback_data="back_to_usercount",
            style="primary",
            icon_custom_emoji_id=PREMIUM["back"]
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های برگشت ==========
# ============================================================
def get_back_button():
    buttons = [
        [InlineKeyboardButton(
            text="بازگشت به منوی اصلی",
            callback_data="back_to_main",
            style="primary",
            icon_custom_emoji_id=PREMIUM["back"]
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های کیف پول ==========
# ============================================================
def get_wallet_buttons():
    buttons = [
        [
            InlineKeyboardButton(
                text="واریز ارزی (تتر/ترون)",
                callback_data="deposit_crypto",
                style="danger",
                icon_custom_emoji_id=PREMIUM["diamond"]
            ),
            InlineKeyboardButton(
                text="واریز ریالی (کارت بانکی)",
                callback_data="deposit_rial",
                style="success",
                icon_custom_emoji_id=PREMIUM["cash"]
            )
        ],
        [
            InlineKeyboardButton(
                text="بازگشت به منوی اصلی",
                callback_data="back_to_main",
                style="primary",
                icon_custom_emoji_id=PREMIUM["back"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های کیف پول پیشرفته ==========
# ============================================================
def get_wallet_advanced_buttons():
    buttons = [
        [
            InlineKeyboardButton(
                text="واریز ارزی",
                callback_data="deposit_crypto",
                style="danger",
                icon_custom_emoji_id=PREMIUM["diamond"]
            ),
            InlineKeyboardButton(
                text="واریز ریالی",
                callback_data="deposit_rial",
                style="success",
                icon_custom_emoji_id=PREMIUM["cash"]
            )
        ],
        [
            InlineKeyboardButton(
                text="نمایش موجودی",
                callback_data="show_balance",
                style="primary",
                icon_custom_emoji_id=PREMIUM["flying_money"]
            ),
            InlineKeyboardButton(
                text="تاریخچه تراکنش‌ها",
                callback_data="transaction_history",
                style="primary",
                icon_custom_emoji_id=PREMIUM["history"]
            )
        ],
        [
            InlineKeyboardButton(
                text="بازگشت به منوی اصلی",
                callback_data="back_to_main",
                style="danger",
                icon_custom_emoji_id=PREMIUM["back"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های ارز ==========
# ============================================================
def get_crypto_buttons():
    buttons = [
        [
            InlineKeyboardButton(
                text="تتر (USDT)",
                callback_data="crypto_tether",
                style="success",
                icon_custom_emoji_id=PREMIUM["coin_tether"]
            ),
            InlineKeyboardButton(
                text="ترون (TRX)",
                callback_data="crypto_tron",
                style="danger",
                icon_custom_emoji_id=PREMIUM["coin_tron"]
            )
        ],
        [
            InlineKeyboardButton(
                text="بازگشت به مرحله قبل",
                callback_data="back_to_wallet",
                style="primary",
                icon_custom_emoji_id=PREMIUM["back"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های برگشت به کیف پول ==========
# ============================================================
def get_back_to_wallet():
    buttons = [
        [InlineKeyboardButton(
            text="بازگشت به کیف پول",
            callback_data="back_to_wallet",
            style="primary",
            icon_custom_emoji_id=PREMIUM["back"]
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های برگشت به منوی اصلی ==========
# ============================================================
def get_back_to_main_menu():
    buttons = [
        [InlineKeyboardButton(
            text="بازگشت به منوی اصلی",
            callback_data="back_to_main",
            style="primary",
            icon_custom_emoji_id=PREMIUM["back"]
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های مدیریت سفارشات ==========
# ============================================================
def get_admin_order_buttons(order_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="تایید و ارسال کانفیگ",
                callback_data=f"approve_order_{order_id}",
                style="success",
                icon_custom_emoji_id=PREMIUM["success"]
            ),
            InlineKeyboardButton(
                text="رد سفارش",
                callback_data=f"reject_order_{order_id}",
                style="danger",
                icon_custom_emoji_id=PREMIUM["danger"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های مدیریت تراکنش‌ها ==========
# ============================================================
def get_admin_transaction_buttons(transaction_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="تایید واریز",
                callback_data=f"approve_transaction_{transaction_id}",
                style="success",
                icon_custom_emoji_id=PREMIUM["success"]
            ),
            InlineKeyboardButton(
                text="رد واریز",
                callback_data=f"reject_transaction_{transaction_id}",
                style="danger",
                icon_custom_emoji_id=PREMIUM["danger"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های پنل ادمین ==========
# ============================================================
def get_admin_panel_buttons():
    buttons = [
        [
            InlineKeyboardButton(
                text="مدیریت کاربران", 
                callback_data="admin_users_manage",
                style="primary",
                icon_custom_emoji_id=PREMIUM["user"]
            )
        ],
        [
            InlineKeyboardButton(
                text="سفارشات", 
                callback_data="admin_view_orders",
                style="success",
                icon_custom_emoji_id=PREMIUM["orders"]
            ),
            InlineKeyboardButton(
                text="واریزی‌ها", 
                callback_data="admin_view_transactions",
                style="primary",
                icon_custom_emoji_id=PREMIUM["flying_money"]
            )
        ],
        [
            InlineKeyboardButton(
                text="نرخ ارز", 
                callback_data="admin_change_rates",
                style="primary",
                icon_custom_emoji_id=PREMIUM["dollar_sign"]
            ),
            InlineKeyboardButton(
                text="ولت و کارت", 
                callback_data="admin_change_wallets",
                style="primary",
                icon_custom_emoji_id=PREMIUM["wallet"]
            )
        ],
        [
            InlineKeyboardButton(
                text="مدیریت محصولات", 
                callback_data="admin_manage_products",
                style="primary",
                icon_custom_emoji_id=PREMIUM["server"]
            )
        ],
        # ================== دکمه جدید گردونه شانس ==================
        [
            InlineKeyboardButton(
                text="🎰 مدیریت گردونه شانس", 
                callback_data="admin_spin_panel",
                style="primary",
                icon_custom_emoji_id=PREMIUM["slot"]
            )
        ],
        # =========================================================
        [
            InlineKeyboardButton(
                text="پیام همگانی", 
                callback_data="admin_broadcast",
                style="success",
                icon_custom_emoji_id=PREMIUM["send"]
            )
        ],
        [
            InlineKeyboardButton(
                text="بازگشت به منو", 
                callback_data="back_to_main",
                style="danger",
                icon_custom_emoji_id=PREMIUM["back"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های مدیریت کاربران ==========
# ============================================================
def get_admin_users_buttons():
    buttons = [
        [
            InlineKeyboardButton(
                text="بن کاربر", 
                callback_data="admin_ban_user",
                style="danger",
                icon_custom_emoji_id=PREMIUM["lock"]
            ),
            InlineKeyboardButton(
                text="آنبن کاربر", 
                callback_data="admin_unban_user",
                style="success",
                icon_custom_emoji_id=PREMIUM["unlock"]
            )
        ],
        [
            InlineKeyboardButton(
                text="بازگشت", 
                callback_data="back_to_admin_panel",
                style="danger",
                icon_custom_emoji_id=PREMIUM["back"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های مدیریت محصولات ==========
# ============================================================
def get_product_management_buttons():
    buttons = [
        [
            InlineKeyboardButton(
                text="افزودن محصول جدید",
                callback_data="admin_add_product",
                style="success",
                icon_custom_emoji_id=PREMIUM["success"]
            )
        ],
        [
            InlineKeyboardButton(
                text="لیست محصولات",
                callback_data="admin_list_products",
                style="primary",
                icon_custom_emoji_id=PREMIUM["chart"]
            )
        ],
        [
            InlineKeyboardButton(
                text="بازگشت به پنل ادمین",
                callback_data="back_to_admin_panel",
                style="danger",
                icon_custom_emoji_id=PREMIUM["back"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های لیست محصولات ==========
# ============================================================
def get_product_list_buttons(products):
    buttons = []
    for product in products:
        status_text = "فعال" if product["is_active"] else "غیرفعال"
        buttons.append([InlineKeyboardButton(
            text=f"{product['name']} - {product['price_per_gb']:,} تومان/گیگ ({status_text})",
            callback_data=f"product_edit_{product['id']}",
            style="primary",
            icon_custom_emoji_id=PREMIUM["server"]
        )])
    
    buttons.append([InlineKeyboardButton(
        text="بازگشت به مدیریت محصولات",
        callback_data="admin_manage_products",
        style="danger",
        icon_custom_emoji_id=PREMIUM["back"]
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های عملیات روی محصول ==========
# ============================================================
def get_product_action_buttons(product_id):
    buttons = [
        [
            InlineKeyboardButton(
                text="ویرایش محصول",
                callback_data=f"product_edit_form_{product_id}",
                style="primary",
                icon_custom_emoji_id=PREMIUM["edit"]
            )
        ],
        [
            InlineKeyboardButton(
                text="حذف محصول",
                callback_data=f"product_delete_{product_id}",
                style="danger",
                icon_custom_emoji_id=PREMIUM["danger"]
            )
        ],
        [
            InlineKeyboardButton(
                text="تغییر وضعیت فعال/غیرفعال",
                callback_data=f"product_toggle_{product_id}",
                style="primary",
                icon_custom_emoji_id=PREMIUM["energy"]
            )
        ],
        [
            InlineKeyboardButton(
                text="بازگشت به لیست محصولات",
                callback_data="admin_list_products",
                style="danger",
                icon_custom_emoji_id=PREMIUM["back"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های انتخاب رنگ ==========
# ============================================================
def get_color_buttons():
    buttons = [
        [
            InlineKeyboardButton(
                text="قرمز (danger)",
                callback_data="color_danger",
                style="danger",
                icon_custom_emoji_id=PREMIUM["danger"]
            ),
            InlineKeyboardButton(
                text="آبی (primary)",
                callback_data="color_primary",
                style="primary",
                icon_custom_emoji_id=PREMIUM["diamond"]
            )
        ],
        [
            InlineKeyboardButton(
                text="سبز (success)",
                callback_data="color_success",
                style="success",
                icon_custom_emoji_id=PREMIUM["success"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های بازگشت به پنل ادمین ==========
# ============================================================
def get_back_to_admin_panel():
    buttons = [
        [InlineKeyboardButton(
            text="بازگشت به پنل ادمین",
            callback_data="back_to_admin_panel",
            style="danger",
            icon_custom_emoji_id=PREMIUM["back"]
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های بازگشت به مدت زمان ==========
# ============================================================
def get_back_to_duration():
    buttons = [
        [InlineKeyboardButton(
            text="بازگشت به انتخاب مدت زمان",
            callback_data="back_to_duration",
            style="primary",
            icon_custom_emoji_id=PREMIUM["back"]
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================
# ========== دکمه‌های بازگشت به تعداد کاربر ==========
# ============================================================
def get_back_to_usercount():
    buttons = [
        [InlineKeyboardButton(
            text="بازگشت به انتخاب تعداد کاربر",
            callback_data="back_to_usercount_from_duration",
            style="primary",
            icon_custom_emoji_id=PREMIUM["back"]
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_ticket_buttons():
    """دکمه‌های منوی تیکت برای کاربر"""
    buttons = [
        [
            InlineKeyboardButton(
                text="📝 ارسال تیکت جدید",
                callback_data="ticket_new",
                style="success",
                icon_custom_emoji_id=PREMIUM["send"]
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 مشاهده تیکت‌های من",
                callback_data="ticket_list",
                style="primary",
                icon_custom_emoji_id=PREMIUM["history"]
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 بازگشت به منوی اصلی",
                callback_data="back_to_main",
                style="danger",
                icon_custom_emoji_id=PREMIUM["back"]
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_ticket_list_buttons(tickets):
    """دکمه‌های لیست تیکت‌ها برای کاربر"""
    buttons = []
    for ticket in tickets:
        status_emoji = "🟢" if ticket["status"] == "open" else "🟡" if ticket["status"] == "answered" else "🔴"
        status_text = "باز" if ticket["status"] == "open" else "پاسخ داده شده" if ticket["status"] == "answered" else "بسته"
        buttons.append([InlineKeyboardButton(
            text=f"{status_emoji} تیکت #{ticket['id']} - {status_text}",
            callback_data=f"ticket_detail_{ticket['id']}",
            style="primary"
        )])
    
    buttons.append([InlineKeyboardButton(
        text="🔙 بازگشت به منوی تیکت",
        callback_data="ticket_menu",
        style="danger"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_ticket_detail_buttons(ticket_id, user_id, is_admin=False):
    """دکمه‌های جزئیات تیکت"""
    buttons = []
    
    if is_admin:
        buttons.append([InlineKeyboardButton(
            text="✏️ پاسخ به تیکت",
            callback_data=f"admin_ticket_answer_{ticket_id}",
            style="success"
        )])
        buttons.append([InlineKeyboardButton(
            text="🔒 بستن تیکت",
            callback_data=f"admin_ticket_close_{ticket_id}",
            style="danger"
        )])
        buttons.append([InlineKeyboardButton(
            text="🗑️ حذف تیکت",
            callback_data=f"admin_ticket_delete_{ticket_id}",
            style="danger"
        )])
    else:
        if ticket_id:
            buttons.append([InlineKeyboardButton(
                text="🔙 بازگشت به لیست تیکت‌ها",
                callback_data="ticket_list",
                style="danger"
            )])
    
    buttons.append([InlineKeyboardButton(
        text="🔙 بازگشت به منوی تیکت",
        callback_data="ticket_menu",
        style="danger"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_ticket_list_buttons(tickets):
    """دکمه‌های لیست تیکت‌ها برای ادمین"""
    buttons = []
    for ticket in tickets:
        status_emoji = "🟢" if ticket["status"] == "open" else "🟡" if ticket["status"] == "answered" else "🔴"
        status_text = "باز" if ticket["status"] == "open" else "پاسخ داده شده" if ticket["status"] == "answered" else "بسته"
        user_display = ticket["first_name"] or ticket["username"] or ticket["user_id"]
        buttons.append([InlineKeyboardButton(
            text=f"#{ticket['id']} - {user_display} ({status_emoji})",
            callback_data=f"admin_ticket_detail_{ticket['id']}",
            style="primary"
        )])
    
    buttons.append([InlineKeyboardButton(
        text="🔙 بازگشت به پنل ادمین",
        callback_data="back_to_admin_panel",
        style="danger"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
