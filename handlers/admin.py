from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import (
    get_db_connection, 
    get_setting, 
    set_setting,
    get_spin_items,
    get_all_spin_items,
    get_spin_item_by_id,
    add_spin_item,
    update_spin_item,
    delete_spin_item,
    toggle_spin_item_status,
    get_total_chance,
    get_user_spin_count,
    mark_spin_for_order,
    get_last_completed_order_id,
    can_user_spin,
    get_all_tickets,
    get_ticket_by_id,
    answer_ticket,
    close_ticket,
    delete_ticket,
    get_open_tickets_count,
    get_all_admins,
    add_admin,
    remove_admin,
    is_user_admin,
    get_referral_settings,        # <-- اضافه کن
    set_referral_setting,         # <-- اضافه کن
    get_top_referrers             # <-- اضافه کن
)
from models import User, Product
from config import ADMIN_ID, BOT_TOKEN
from datetime import datetime, timedelta
import asyncio

router = Router()
bot = Bot(token=BOT_TOKEN)

# ================== دیکشنری ایموجی‌های پرمیوم ==================
PREMIUM = {
    "admin": "6084723220995381369",
    "user": "6219810752887262728",
    "orders": "4970023558068568720",
    "money": "5400254220270055279",
    "diamond": "6084795634143990713",
    "success": "6298804341151107148",
    "danger": "5771395074600472173",
    "back": "6087055285157893604",
    "loading": "6084846396362462760",
    "star": "5978776771623914876",
    "chart": "6084890063294959714",
    "top": "6084890063294959714",
    "time": "5971895340662526314",
    "energy": "6084367318530397918",
    "flying_money": "5399868497847135951",
    "premium_star": "5978776771623914876",
    "mouse_click": "5400286088927392515",
    "exclamation": "6084463229445085650",
    "earth": "5397798946380721942",
    "fire": "5400233320959191625",
    "winner": "4985741377435337443",
    "gift": "4985741377435337443",
    "percent": "6086889112873210296",
    "lock": "5400250874490532265",
    "unlock": "6298804341151107148",
    "alert": "4990219185784095465",
    "shield": "5033242607627535090",
    "flag": "4969862428075491925",
    "wallet": "4967518033061872209",
    "shopping": "5033300671290409647",
    "server": "6084478403564541578",
    "dollar_sign": "5400247352617349412",
    "coin_tether": "5949395935439099112",
    "coin_tron": "5949382251673292713",
    "edit": "6086723567653753735",
    "spray": "4981418681830475148",
    "info": "6087054662387635231",
    "send": "6087055285157893604",
    "heart": "5397699333204226798",
    "slot": "5400585043394618397",
    "cash": "6084573665939166516",
    "support": "5971889748615105853",
    "history": "6084890063294959714",
    "rules": "4985841557547516692",
    "settings": "6086723567653753735",
    "stats": "6084890063294959714",
    "report": "6084573665939166516",
    "wallet_manage": "4967518033061872209",
    "customize": "6086723567653753735",
    "force_join": "6084478403564541578",
    "today": "4990219185784095465",
    "week": "5399868497847135951",
    "month": "5397798946380721942",
    "total": "5986324716336068034",
    "new": "4970086827231806362"
}

class AdminStates(StatesGroup):
    waiting_for_ban_user_id = State()
    waiting_for_unban_user_id = State()
    waiting_for_new_tether_rate = State()
    waiting_for_new_tron_rate = State()
    waiting_for_new_tether_wallet = State()
    waiting_for_new_tron_wallet = State()
    waiting_for_new_card = State()
    waiting_for_order_config = State()
    waiting_for_product_name = State()
    waiting_for_product_price = State()
    waiting_for_product_color = State()
    waiting_for_edit_product_name = State()
    waiting_for_edit_product_price = State()
    waiting_for_edit_product_color = State()
    waiting_for_broadcast_message = State()
    waiting_for_spin_item_name = State()
    waiting_for_spin_item_chance = State()
    waiting_for_spin_item_description = State()
    waiting_for_edit_spin_item_name = State()
    waiting_for_edit_spin_item_chance = State()
    waiting_for_edit_spin_item_description = State()
    waiting_for_ticket_answer = State()
    waiting_for_force_join_channel_id = State()
    waiting_for_force_join_channel_link = State()
    waiting_for_wallet_user_id = State()
    waiting_for_wallet_amount = State()
    waiting_for_ref_amount = State()
    waiting_for_ref_discount = State()
    waiting_for_edit_start_text = State()
    waiting_for_edit_rules_text = State()
    waiting_for_add_admin_id = State()

temp_admin_data = {}

# ==================== توابع کمکی ====================

def get_back_to_admin_panel_buttons():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔙 بازگشت به پنل ادمین",
            callback_data="back_to_admin_panel",
            style="danger"
        )]
    ])

def get_admin_panel_buttons():
    buttons = [
        [InlineKeyboardButton(text="👤 مدیریت کاربران", callback_data="admin_users_manage", style="primary")],
        [InlineKeyboardButton(text="👑 مدیریت ادمین‌ها", callback_data="admin_admins_manage", style="primary")],
        [InlineKeyboardButton(text="🛍️ سفارشات", callback_data="admin_view_orders", style="success"),
         InlineKeyboardButton(text="💸 واریزی‌ها", callback_data="admin_view_transactions", style="primary")],
        [InlineKeyboardButton(text="🎫 مدیریت تیکت‌ها", callback_data="admin_tickets_panel", style="primary")],
        [InlineKeyboardButton(text="📊 وضعیت ربات", callback_data="admin_status", style="primary"),
         InlineKeyboardButton(text="📈 آمار", callback_data="admin_stats", style="primary")],
        [InlineKeyboardButton(text="📊 گزارش فروشگاه", callback_data="admin_shop_report", style="primary")],
        [InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="admin_settings", style="primary")],
        [InlineKeyboardButton(text="💳 مدیریت کیف پول", callback_data="admin_wallet_manage", style="primary")],
        [InlineKeyboardButton(text="🎨 شخصی‌سازی", callback_data="admin_customize", style="primary")],
        [InlineKeyboardButton(text="🔗 جوین اجباری", callback_data="admin_force_join", style="primary")],
        [InlineKeyboardButton(text="🎰 مدیریت گردونه شانس", callback_data="admin_spin_panel", style="primary")],
        [InlineKeyboardButton(text="🔧 مدیریت محصولات", callback_data="admin_manage_products", style="primary")],
        [InlineKeyboardButton(text="🔗 مدیریت رفرال", callback_data="admin_referral_settings", style="primary")],
        [InlineKeyboardButton(text="💰 تغییر نرخ ارز", callback_data="admin_change_rates", style="primary"),
         InlineKeyboardButton(text="💳 تغییر ولت و کارت", callback_data="admin_change_wallets", style="primary")],
        [InlineKeyboardButton(text="📤 پیام همگانی", callback_data="admin_broadcast", style="success")],
        [InlineKeyboardButton(text="🔙 بازگشت به منو", callback_data="back_to_main", style="danger")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==================== 1. پنل اصلی ادمین ====================
@router.message(F.text == "👑 پنل ادمین")
async def admin_panel(message: Message):
    user_id = message.from_user.id
    
    if not is_user_admin(user_id):
        await message.answer(
            f'💀 <b>شما دسترسی به این بخش ندارید!</b>',
            parse_mode='HTML'
        )
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
    pending_orders = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM transactions WHERE status = 'pending'")
    pending_transactions = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE status = 'approved'")
    total_deposits = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE is_active = 1")
    active_products = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending' OR status = 'paid'")
    total_processing = cursor.fetchone()[0] or 0
    
    open_tickets = get_open_tickets_count()
    conn.close()
    
    text = (
        f'🟣 <b>پنل مدیریت پیشرفته</b>\n'
        f'💎 {"─" * 20}\n\n'
        f'🔝 <b>آمار کلی:</b>\n\n'
        f'👤 کل کاربران: <b>{total_users:,}</b> نفر\n'
        f'🛍️ سفارشات در انتظار: <b>{pending_orders}</b>\n'
        f'🥶 در حال پردازش: <b>{total_processing}</b>\n'
        f'💸 واریزی در انتظار: <b>{pending_transactions}</b>\n'
        f'🥇 کل واریزی‌ها: <b>{total_deposits:,}</b> تومان\n'
        f'🔗 محصولات فعال: <b>{active_products}</b>\n'
        f'🎫 تیکت‌های باز: <b>{open_tickets}</b>\n\n'
        f'🖱 از منوی زیر مدیریت کن:'
    )
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_admin_panel_buttons())


# ==================== 2. مدیریت کاربران ====================
@router.callback_query(F.data == "admin_users_manage")
async def admin_users_manage(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔒 بن کاربر", callback_data="admin_ban_user", style="danger")],
        [InlineKeyboardButton(text="🔓 آنبن کاربر", callback_data="admin_unban_user", style="success")],
        [InlineKeyboardButton(text="📋 لیست کاربران بن شده", callback_data="admin_banned_users_list", style="primary")],
        [InlineKeyboardButton(text="🔙 بازگشت به پنل ادمین", callback_data="back_to_admin_panel", style="danger")]
    ])
    
    await callback.message.delete()
    await callback.message.answer(
        f'👤 <b>مدیریت کاربران</b>\n\n'
        f'🖱 از منوی زیر یکی رو انتخاب کن:',
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "admin_banned_users_list")
async def admin_banned_users_list(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, first_name, username FROM users WHERE is_banned = 1")
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        await callback.message.delete()
        await callback.message.answer(
            f'ℹ️ <b>هیچ کاربر بن شده‌ای وجود ندارد!</b>',
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_users_manage", style="danger")]
            ])
        )
        await callback.answer()
        return
    
    text = f'🔒 <b>لیست کاربران بن شده</b>\n\n'
    for user in users:
        text += f'• {user["first_name"]} (@{user["username"] or "ندارد"}) - آیدی: <code>{user["user_id"]}</code>\n'
    
    await callback.message.delete()
    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_users_manage", style="danger")]
        ])
    )
    await callback.answer()


# ==================== 3. مدیریت ادمین‌ها ====================
@router.callback_query(F.data == "admin_admins_manage")
async def admin_admins_manage(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ افزودن ادمین جدید", callback_data="admin_add_admin", style="success")],
        [InlineKeyboardButton(text="📋 لیست ادمین‌ها", callback_data="admin_list_admins", style="primary")],
        [InlineKeyboardButton(text="🔙 بازگشت به پنل ادمین", callback_data="back_to_admin_panel", style="danger")]
    ])
    
    await callback.message.delete()
    await callback.message.answer(
        f'👑 <b>مدیریت ادمین‌ها</b>\n\n'
        f'🖱 از منوی زیر یکی رو انتخاب کن:\n\n'
        f'ℹ️ <b>نکته:</b> ادمین اصلی (شما) قابل حذف نیستید.',
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add_admin")
async def admin_add_admin_start(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'➕ <b>افزودن ادمین جدید</b>\n\n'
        f'🖱 آیدی عددی کاربر رو وارد کن:\n'
        f'‼️ مثال: <code>123456789</code>\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_add_admin_id)
    await callback.answer()


@router.message(AdminStates.waiting_for_add_admin_id)
async def process_add_admin(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            f'🚨 <b>آیدی عددی معتبر وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    if user_id == ADMIN_ID:
        await message.answer(
            f'ℹ️ <b>شما خودتان ادمین اصلی هستید!</b>',
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, username, is_admin FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        await message.answer(
            f'🚨 <b>کاربر با آیدی {user_id} یافت نشد!</b>\n\n'
            f'🖱 لطفاً مطمئن شوید کاربر ربات را استارت کرده باشد.',
            parse_mode="HTML"
        )
        conn.close()
        await state.clear()
        return
    
    if user["is_admin"]:
        await message.answer(
            f'ℹ️ <b>کاربر {user["first_name"]} قبلاً ادمین است!</b>',
            parse_mode="HTML"
        )
        conn.close()
        await state.clear()
        return
    
    add_admin(user_id)
    conn.close()
    
    try:
        await bot.send_message(
            user_id,
            f'👑 <b>شما به عنوان ادمین ربات انتخاب شدید!</b>\n\n'
            f'🖱 از این پس میتوانید از پنل ادمین استفاده کنید.\n'
            f'📱 دستور /start را بزنید تا منوی ادمین برای شما نمایش داده شود.',
            parse_mode="HTML"
        )
    except:
        pass
    
    await message.answer(
        f'✅ <b>کاربر {user["first_name"]} با موفقیت به عنوان ادمین اضافه شد!</b>\n\n'
        f'👤 نام: {user["first_name"]}\n'
        f'🟣 یوزرنیم: @{user["username"] or "ندارد"}\n'
        f'🔝 آیدی: <code>{user_id}</code>',
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به مدیریت ادمین‌ها", callback_data="admin_admins_manage", style="danger")]
        ])
    )
    await state.clear()


@router.callback_query(F.data == "admin_list_admins")
async def admin_list_admins(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    admins = get_all_admins()
    
    if not admins:
        await callback.message.delete()
        await callback.message.answer(
            f'ℹ️ <b>هیچ ادمینی یافت نشد!</b>',
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_admins_manage", style="danger")]
            ])
        )
        await callback.answer()
        return
    
    text = f'👑 <b>لیست ادمین‌ها</b>\n\n'
    
    for admin in admins:
        is_owner = "⭐ " if admin["user_id"] == ADMIN_ID else ""
        text += f'{is_owner}• {admin["first_name"]} (@{admin["username"] or "ندارد"}) - آیدی: <code>{admin["user_id"]}</code>\n'
    
    text += f'\nℹ️ <b>تعداد:</b> {len(admins)} نفر'
    
    buttons = []
    for admin in admins:
        if admin["user_id"] != ADMIN_ID:
            buttons.append([InlineKeyboardButton(
                text=f"🗑️ حذف {admin['first_name']}",
                callback_data=f"admin_remove_admin_{admin['user_id']}",
                style="danger"
            )])
    
    buttons.append([InlineKeyboardButton(
        text="🔙 بازگشت به مدیریت ادمین‌ها",
        callback_data="admin_admins_manage",
        style="danger"
    )])
    
    await callback.message.delete()
    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_remove_admin_"))
async def admin_remove_admin(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    user_id = int(callback.data.split("_")[3])
    
    if user_id == ADMIN_ID:
        await callback.answer(
            f'⚠️ شما نمیتوانید خودتان را حذف کنید!',
            show_alert=True
        )
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        await callback.answer(
            f'🚨 کاربر یافت نشد!',
            show_alert=True
        )
        return
    
    remove_admin(user_id)
    
    try:
        await bot.send_message(
            user_id,
            f'⚠️ <b>دسترسی ادمین شما حذف شد!</b>\n\n'
            f'🖱 دیگر به پنل ادمین دسترسی ندارید.\n'
            f'📱 برای استفاده از بخش‌های عادی ربات، /start را بزنید.',
            parse_mode="HTML"
        )
    except:
        pass
    
    await callback.message.delete()
    await callback.message.answer(
        f'✅ <b>دسترسی ادمین کاربر {user["first_name"]} با موفقیت حذف شد!</b>',
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به لیست ادمین‌ها", callback_data="admin_list_admins", style="danger")]
        ])
    )
    await callback.answer()


# ==================== 4. تنظیمات ====================
@router.callback_query(F.data == "admin_settings")
async def admin_settings(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 ریستارت ربات", callback_data="admin_restart_bot", style="danger")],
        [InlineKeyboardButton(text="🔓 آنبن همه کاربران", callback_data="admin_unban_all_users", style="danger")],
        [InlineKeyboardButton(text="🔙 بازگشت به پنل ادمین", callback_data="back_to_admin_panel", style="danger")]
    ])
    
    await callback.message.delete()
    await callback.message.answer(
        f'⚙️ <b>تنظیمات ربات</b>\n\n'
        f'🖱 از منوی زیر یکی رو انتخاب کن:',
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "admin_unban_all_users")
async def admin_unban_all_users(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, first_name FROM users WHERE is_banned = 1")
    banned_users = cursor.fetchall()
    
    if not banned_users:
        await callback.answer('ℹ️ هیچ کاربر بن شده‌ای وجود ندارد!', show_alert=True)
        return
    
    cursor.execute("UPDATE users SET is_banned = 0 WHERE is_banned = 1")
    conn.commit()
    conn.close()
    
    for user in banned_users:
        try:
            await bot.send_message(
                user["user_id"],
                f'🔓 <b>حساب شما توسط ادمین آنبن شد!</b>\n\n'
                f'🖱 میتونی دوباره از خدمات ربات استفاده کنی.',
                parse_mode="HTML"
            )
        except:
            pass
    
    await callback.message.delete()
    await callback.message.answer(
        f'✅ <b>همه کاربران بن شده با موفقیت آنبن شدند!</b>\n\n'
        f'👤 تعداد: <b>{len(banned_users)}</b> نفر',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_restart_bot")
async def admin_restart_bot(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    await callback.message.delete()
    msg = await callback.message.answer(
        f'🔄 <b>ربات در حال ریستارت...</b>\n\n'
        f'⏳ لطفاً ۵ ثانیه صبر کنید...',
        parse_mode="HTML"
    )
    
    await asyncio.sleep(5)
    
    await msg.edit_text(
        f'✅ <b>ربات با موفقیت ریستارت شد!</b>\n\n'
        f'🟢 ربات آنلاین است.',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await callback.answer()


# ==================== 5. وضعیت ربات ====================
@router.callback_query(F.data == "admin_status")
async def admin_status(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_banned = 0")
    active_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
    pending_orders = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
    open_tickets = cursor.fetchone()[0]
    conn.close()
    
    text = (
        f'📊 <b>وضعیت کلی ربات</b>\n\n'
        f'💎 {"─" * 20}\n\n'
        f'✅ <b>وضعیت ربات:</b> 🟢 آنلاین\n'
        f'🔄 <b>آخرین آپدیت:</b> <code>v2.0.0</code>\n'
        f'🛒 <b>وضعیت فروشگاه:</b> 🟢 باز\n'
        f'👤 <b>کل کاربران:</b> {total_users:,}\n'
        f'✅ <b>کاربران فعال:</b> {active_users:,}\n'
        f'🥶 <b>سفارشات در انتظار:</b> {pending_orders}\n'
        f'🎫 <b>تیکت‌های باز:</b> {open_tickets}\n\n'
        f'❤️ <b>پینگ ربات:</b> <code>پینگ</code>'
    )
    
    await callback.message.delete()
    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await callback.answer()


# ==================== 6. آمار ====================
@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_banned = 0")
    active_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_banned = 1")
    banned_users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')")
    new_users_month = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE strftime('%Y-%W', created_at) = strftime('%Y-%W', 'now')")
    new_users_week = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE date(created_at) = date('now')")
    new_users_today = cursor.fetchone()[0]
    
    conn.close()
    
    text = (
        f'📈 <b>آمار کامل ربات</b>\n\n'
        f'💎 {"─" * 20}\n\n'
        f'👤 <b>کل کاربران:</b> {total_users:,}\n'
        f'✅ <b>کاربران فعال:</b> {active_users:,}\n'
        f'💀 <b>کاربران بن شده:</b> {banned_users:,}\n\n'
        f'🆕 <b>کاربران جدید:</b>\n'
        f'• امروز: <b>{new_users_today}</b>\n'
        f'• این هفته: <b>{new_users_week}</b>\n'
        f'• این ماه: <b>{new_users_month}</b>'
    )
    
    await callback.message.delete()
    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await callback.answer()


# ==================== 7. گزارش فروشگاه ====================
@router.callback_query(F.data == "admin_shop_report")
async def admin_shop_report(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*), SUM(total_price) FROM orders WHERE date(created_at) = date('now') AND status = 'completed'")
    today = cursor.fetchone()
    today_count = today[0] or 0
    today_amount = today[1] or 0
    
    cursor.execute("SELECT COUNT(*), SUM(total_price) FROM orders WHERE strftime('%Y-%W', created_at) = strftime('%Y-%W', 'now') AND status = 'completed'")
    week = cursor.fetchone()
    week_count = week[0] or 0
    week_amount = week[1] or 0
    
    cursor.execute("SELECT COUNT(*), SUM(total_price) FROM orders WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now') AND status = 'completed'")
    month = cursor.fetchone()
    month_count = month[0] or 0
    month_amount = month[1] or 0
    
    cursor.execute("SELECT COUNT(*), SUM(total_price) FROM orders WHERE status = 'completed'")
    total = cursor.fetchone()
    total_count = total[0] or 0
    total_amount = total[1] or 0
    
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
    pending = cursor.fetchone()[0] or 0
    
    conn.close()
    
    text = (
        f'📊 <b>گزارش فروشگاه</b>\n\n'
        f'💎 {"─" * 20}\n\n'
        f'📅 <b>فروش امروز:</b>\n'
        f'• تعداد: {today_count} سفارش\n'
        f'• مبلغ: {today_amount:,.0f} تومان\n\n'
        f'📅 <b>فروش این هفته:</b>\n'
        f'• تعداد: {week_count} سفارش\n'
        f'• مبلغ: {week_amount:,.0f} تومان\n\n'
        f'📅 <b>فروش این ماه:</b>\n'
        f'• تعداد: {month_count} سفارش\n'
        f'• مبلغ: {month_amount:,.0f} تومان\n\n'
        f'💰 <b>کل فروش:</b>\n'
        f'• تعداد: {total_count} سفارش\n'
        f'• مبلغ: {total_amount:,.0f} تومان\n\n'
        f'🥶 <b>سفارشات در انتظار:</b> {pending}'
    )
    
    await callback.message.delete()
    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await callback.answer()


# ==================== 8. مدیریت کیف پول ====================
@router.callback_query(F.data == "admin_wallet_manage")
async def admin_wallet_manage(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'💳 <b>مدیریت کیف پول</b>\n\n'
        f'🖱 آیدی عددی کاربر رو وارد کن:\n'
        f'‼️ مثال: <code>123456789</code>\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_wallet_user_id)
    await callback.answer()


@router.message(AdminStates.waiting_for_wallet_user_id)
async def process_wallet_user_id(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            f'🚨 <b>آیدی عددی معتبر وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    user = User.get_user(user_id)
    if not user:
        await message.answer(
            f'🚨 <b>کاربر با آیدی {user_id} یافت نشد!</b>',
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    temp_admin_data["wallet_user_id"] = user_id
    balance = User.get_balance(user_id)
    
    await message.answer(
        f'👤 <b>کاربر: {user["first_name"]}</b>\n'
        f'🔝 آیدی: <code>{user_id}</code>\n'
        f'💳 موجودی فعلی: <b>{balance:,}</b> تومان\n\n'
        f'🖱 مقدار جدید موجودی رو به تومان وارد کن:\n'
        f'‼️ مثال: 50000\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_wallet_amount)


@router.message(AdminStates.waiting_for_wallet_amount)
async def process_wallet_amount(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        if "wallet_user_id" in temp_admin_data:
            del temp_admin_data["wallet_user_id"]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    try:
        amount = int(message.text.strip().replace(",", "").replace(" ", ""))
        if amount < 0:
            raise ValueError
    except ValueError:
        await message.answer(
            f'🚨 <b>لطفاً یک عدد معتبر وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    user_id = temp_admin_data.get("wallet_user_id")
    if not user_id:
        await message.answer(
            f'🚨 <b>خطا! لطفاً دوباره تلاش کن.</b>',
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    User.update_balance(user_id, amount - User.get_balance(user_id))
    
    await message.answer(
        f'✅ <b>موجودی کاربر با موفقیت تغییر کرد!</b>\n\n'
        f'👤 آیدی کاربر: <code>{user_id}</code>\n'
        f'💳 موجودی جدید: <b>{amount:,}</b> تومان',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    
    del temp_admin_data["wallet_user_id"]
    await state.clear()


# ==================== 9. شخصی‌سازی ====================
@router.callback_query(F.data == "admin_customize")
async def admin_customize(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 ویرایش متن استارت", callback_data="admin_edit_start_text", style="primary")],
        [InlineKeyboardButton(text="📝 ویرایش قوانین و مقررات", callback_data="admin_edit_rules_text", style="primary")],
        [InlineKeyboardButton(text="🔙 بازگشت به پنل ادمین", callback_data="back_to_admin_panel", style="danger")]
    ])
    
    await callback.message.delete()
    await callback.message.answer(
        f'🎨 <b>شخصی‌سازی ربات</b>\n\n'
        f'🖱 متن مورد نظر رو انتخاب کن تا ویرایش کنی:',
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "admin_edit_start_text")
async def admin_edit_start_text(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    current_text = get_setting("start_text") or "متن استارت تنظیم نشده"
    
    await callback.message.delete()
    await callback.message.answer(
        f'✏️ <b>ویرایش متن استارت</b>\n\n'
        f'ℹ️ متن فعلی:\n<code>{current_text}</code>\n\n'
        f'🖱 متن جدید رو وارد کن:\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_edit_start_text)
    await callback.answer()


@router.message(AdminStates.waiting_for_edit_start_text)
async def process_edit_start_text(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    set_setting("start_text", message.text)
    
    await message.answer(
        f'✅ <b>متن استارت با موفقیت تغییر کرد!</b>',
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به شخصی‌سازی", callback_data="admin_customize", style="danger")]
        ])
    )
    await state.clear()


@router.callback_query(F.data == "admin_edit_rules_text")
async def admin_edit_rules_text(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    current_text = get_setting("rules_text") or "متن قوانین تنظیم نشده"
    
    await callback.message.delete()
    await callback.message.answer(
        f'✏️ <b>ویرایش قوانین و مقررات</b>\n\n'
        f'ℹ️ متن فعلی:\n<code>{current_text}</code>\n\n'
        f'🖱 متن جدید رو وارد کن:\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_edit_rules_text)
    await callback.answer()


@router.message(AdminStates.waiting_for_edit_rules_text)
async def process_edit_rules_text(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    set_setting("rules_text", message.text)
    
    await message.answer(
        f'✅ <b>متن قوانین با موفقیت تغییر کرد!</b>',
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به شخصی‌سازی", callback_data="admin_customize", style="danger")]
        ])
    )
    await state.clear()


# ==================== 10. جوین اجباری ====================
@router.callback_query(F.data == "admin_force_join")
async def admin_force_join(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    current_channel = get_setting("force_join_channel") or "تنظیم نشده"
    current_name = get_setting("force_join_name") or "تنظیم نشده"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑️ حذف جوین اجباری", callback_data="admin_remove_force_join", style="danger")],
        [InlineKeyboardButton(text="🔙 بازگشت به پنل ادمین", callback_data="back_to_admin_panel", style="danger")]
    ])
    
    await callback.message.delete()
    await callback.message.answer(
        f'🔗 <b>تنظیمات جوین اجباری</b>\n\n'
        f'ℹ️ کانال فعلی: <code>{current_channel}</code>\n'
        f'ℹ️ نام نمایشی: <code>{current_name}</code>\n\n'
        f'‼️ <b>نکات مهم:</b>\n'
        f'• برای کانال <b>عمومی</b>: یوزرنیم کانال رو با @ وارد کن (مثال: @channel)\n'
        f'• برای کانال <b>خصوصی</b>: لینک دعوت کانال رو وارد کن (مثال: https://t.me/joinchat/xxxxx)\n'
        f'• ربات باید در کانال ادمین باشد!\n\n'
        f'🖱 یوزرنیم یا لینک کانال رو وارد کن:\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await state.set_state(AdminStates.waiting_for_force_join_channel_link)
    await callback.answer()


@router.callback_query(F.data == "admin_remove_force_join")
async def admin_remove_force_join(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    set_setting("force_join_channel", "")
    set_setting("force_join_name", "")
    
    await callback.message.delete()
    await callback.message.answer(
        f'✅ <b>جوین اجباری با موفقیت حذف شد!</b>',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await callback.answer()


@router.message(AdminStates.waiting_for_force_join_channel_link)
async def process_force_join_channel_link(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    channel_input = message.text.strip()
    channel_id = None
    channel_name = None
    
    try:
        if channel_input.startswith("https://t.me/joinchat/") or channel_input.startswith("t.me/joinchat/"):
            temp_admin_data["force_join_link"] = channel_input
            await message.answer(
                f'ℹ️ <b>لینک کانال خصوصی دریافت شد!</b>\n\n'
                f'‼️ برای کانال خصوصی، آیدی عددی کانال رو هم وارد کن:\n'
                f'🖱 مثال: <code>-1001234567890</code>\n\n'
                f'ℹ️ <b>نکته:</b> برای دریافت آیدی عددی کانال، از ربات @userinfobot استفاده کن.',
                parse_mode="HTML",
                reply_markup=get_back_to_admin_panel_buttons()
            )
            await state.set_state(AdminStates.waiting_for_force_join_channel_id)
            return
            
        elif channel_input.startswith("-100") or channel_input.isdigit():
            channel_id = channel_input
            chat = await bot.get_chat(channel_id)
            channel_name = chat.title
            
            member = await bot.get_chat_member(channel_id, bot.id)
            if member.status not in ["administrator", "creator"]:
                await message.answer(
                    f'🚨 <b>ربات در این کانال ادمین نیست!</b>\n\n'
                    f'🖱 لطفاً ابتدا ربات را به عنوان ادمین به کانال اضافه کن و دوباره تلاش کن.',
                    parse_mode="HTML"
                )
                return
            
        elif channel_input.startswith("@"):
            chat = await bot.get_chat(channel_input)
            channel_id = str(chat.id)
            channel_name = chat.title
            
            member = await bot.get_chat_member(channel_input, bot.id)
            if member.status not in ["administrator", "creator"]:
                await message.answer(
                    f'🚨 <b>ربات در این کانال ادمین نیست!</b>\n\n'
                    f'🖱 لطفاً ابتدا ربات را به عنوان ادمین به کانال اضافه کن و دوباره تلاش کن.',
                    parse_mode="HTML"
                )
                return
        else:
            await message.answer(
                f'🚨 <b>فرمت ورودی نامعتبر!</b>\n\n'
                f'🖱 لطفاً یکی از موارد زیر رو وارد کن:\n'
                f'• یوزرنیم کانال عمومی: <code>@channel</code>\n'
                f'• لینک دعوت کانال خصوصی: <code>https://t.me/joinchat/xxxxx</code>\n'
                f'• آیدی عددی کانال: <code>-1001234567890</code>',
                parse_mode="HTML"
            )
            return
    
    except Exception as e:
        await message.answer(
            f'🚨 <b>خطا در ارتباط با کانال!</b>\n\n'
            f'ℹ️ خطا: {str(e)}\n\n'
            f'🖱 لطفاً دوباره تلاش کن.',
            parse_mode="HTML"
        )
        return
    
    if channel_id and channel_name:
        set_setting("force_join_channel", channel_id)
        set_setting("force_join_name", channel_name)
        
        await message.answer(
            f'✅ <b>جوین اجباری با موفقیت تنظیم شد!</b>\n\n'
            f'🔗 کانال: <b>{channel_name}</b>\n'
            f'🔝 آیدی: <code>{channel_id}</code>\n\n'
            f'🖱 کاربران برای استفاده از ربات باید عضو این کانال باشند.',
            parse_mode="HTML",
            reply_markup=get_back_to_admin_panel_buttons()
        )
        await state.clear()


@router.message(AdminStates.waiting_for_force_join_channel_id)
async def process_force_join_channel_id(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        if "force_join_link" in temp_admin_data:
            del temp_admin_data["force_join_link"]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    channel_id = message.text.strip()
    
    try:
        chat = await bot.get_chat(channel_id)
        channel_name = chat.title
        
        member = await bot.get_chat_member(channel_id, bot.id)
        if member.status not in ["administrator", "creator"]:
            await message.answer(
                f'🚨 <b>ربات در این کانال ادمین نیست!</b>\n\n'
                f'🖱 لطفاً ابتدا ربات را به عنوان ادمین به کانال اضافه کن و دوباره تلاش کن.',
                parse_mode="HTML"
            )
            return
        
        set_setting("force_join_channel", channel_id)
        set_setting("force_join_name", channel_name)
        
        await message.answer(
            f'✅ <b>جوین اجباری با موفقیت تنظیم شد!</b>\n\n'
            f'🔗 کانال: <b>{channel_name}</b>\n'
            f'🔝 آیدی: <code>{channel_id}</code>\n\n'
            f'🖱 کاربران برای استفاده از ربات باید عضو این کانال باشند.',
            parse_mode="HTML",
            reply_markup=get_back_to_admin_panel_buttons()
        )
        
        if "force_join_link" in temp_admin_data:
            del temp_admin_data["force_join_link"]
        await state.clear()
        
    except Exception as e:
        await message.answer(
            f'🚨 <b>خطا در ارتباط با کانال!</b>\n\n'
            f'ℹ️ خطا: {str(e)}\n\n'
            f'🖱 لطفاً آیدی عددی معتبر وارد کن.',
            parse_mode="HTML"
        )


# ==================== 11. بن/آنبن کاربر ====================
@router.callback_query(F.data == "admin_ban_user")
async def admin_ban_user(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'🔒 <b>بن کردن کاربر</b>\n\n'
        f'🖱 آیدی عددی کاربر رو وارد کن:\n'
        f'‼️ مثال: <code>123456789</code>\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_ban_user_id)
    await callback.answer()


@router.message(AdminStates.waiting_for_ban_user_id)
async def process_ban_user(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            f'🚨 <b>آیدی عددی معتبر وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    if user_id == ADMIN_ID:
        await message.answer(
            f'🚨 <b>نمیتونی ادمین رو بن کنی!</b>',
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, is_banned FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        await message.answer(
            f'🚨 <b>کاربر با آیدی {user_id} یافت نشد!</b>',
            parse_mode="HTML"
        )
        conn.close()
        await state.clear()
        return
    
    if user["is_banned"]:
        await message.answer(
            f'ℹ️ <b>کاربر {user["first_name"]} قبلاً بن شده!</b>',
            parse_mode="HTML"
        )
        conn.close()
        await state.clear()
        return
    
    cursor.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    cursor.execute("INSERT INTO admin_logs (admin_id, action, target_user_id, details) VALUES (?, 'ban', ?, ?)",
                   (ADMIN_ID, user_id, f"کاربر {user['first_name']} توسط ادمین بن شد"))
    conn.commit()
    conn.close()
    
    try:
        await bot.send_message(
            user_id,
            f'🔒 <b>حساب شما توسط ادمین مسدود شد!</b>\n\n'
            f'💻 در صورت اعتراض با پشتیبانی تماس بگیرید.',
            parse_mode="HTML"
        )
    except:
        pass
    
    await message.answer(
        f'✅ <b>کاربر {user["first_name"]} با موفقیت بن شد!</b>\n\n'
        f'🔝 آیدی: <code>{user_id}</code>',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.clear()


@router.callback_query(F.data == "admin_unban_user")
async def admin_unban_user(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'🔓 <b>آنبن کردن کاربر</b>\n\n'
        f'🖱 آیدی عددی کاربر رو وارد کن:\n'
        f'‼️ مثال: <code>123456789</code>\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_unban_user_id)
    await callback.answer()


@router.message(AdminStates.waiting_for_unban_user_id)
async def process_unban_user(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            f'🚨 <b>آیدی عددی معتبر وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT first_name, is_banned FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        await message.answer(
            f'🚨 <b>کاربر با آیدی {user_id} یافت نشد!</b>',
            parse_mode="HTML"
        )
        conn.close()
        await state.clear()
        return
    
    if not user["is_banned"]:
        await message.answer(
            f'ℹ️ <b>کاربر {user["first_name"]} در حالت عادی هست!</b>',
            parse_mode="HTML"
        )
        conn.close()
        await state.clear()
        return
    
    cursor.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    cursor.execute("INSERT INTO admin_logs (admin_id, action, target_user_id, details) VALUES (?, 'unban', ?, ?)",
                   (ADMIN_ID, user_id, f"کاربر {user['first_name']} توسط ادمین آنبن شد"))
    conn.commit()
    conn.close()
    
    try:
        await bot.send_message(
            user_id,
            f'🔓 <b>حساب شما توسط ادمین فعال شد!</b>\n\n'
            f'🖱 میتونی دوباره از خدمات ربات استفاده کنی.',
            parse_mode="HTML"
        )
    except:
        pass
    
    await message.answer(
        f'✅ <b>کاربر {user["first_name"]} با موفقیت آنبن شد!</b>',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.clear()


# ==================== 12. پیام همگانی ====================
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'📤 <b>ارسال پیام همگانی</b>\n\n'
        f'🖱 پیام خود را وارد کنید:\n\n'
        f'‼️ پیام به <b>همه کاربران</b> ارسال خواهد شد.\n'
        f'❤️ می‌توانید متن، عکس، فایل یا هر چیز دیگری ارسال کنید.\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_broadcast_message)
    await callback.answer()


@router.message(AdminStates.waiting_for_broadcast_message)
async def process_broadcast(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE is_banned = 0")
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        await message.answer(
            f'🚨 <b>هیچ کاربر فعالی وجود ندارد!</b>',
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    sent = 0
    failed = 0
    
    status_msg = await message.answer(
        f'🥶 <b>در حال ارسال پیام به {len(users)} کاربر...</b>',
        parse_mode="HTML"
    )
    
    for user in users:
        try:
            await bot.copy_message(
                chat_id=user["user_id"],
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            sent += 1
        except:
            failed += 1
        
        if sent % 20 == 0:
            await status_msg.edit_text(
                f'🥶 <b>در حال ارسال...</b>\n\n'
                f'✅ موفق: {sent}\n'
                f'💀 ناموفق: {failed}'
            )
        await asyncio.sleep(0.05)
    
    await status_msg.edit_text(
        f'✅ <b>ارسال همگانی تمام شد!</b>\n\n'
        f'📤 موفق: <b>{sent}</b>\n'
        f'💀 ناموفق: <b>{failed}</b>',
        parse_mode="HTML"
    )
    await state.clear()


# ==================== 13. مشاهده سفارشات ====================
@router.callback_query(F.data == "admin_view_orders")
async def admin_view_orders(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, u.first_name, u.username 
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        WHERE o.status = 'pending'
        ORDER BY o.id DESC
    """)
    orders = cursor.fetchall()
    conn.close()
    
    if not orders:
        await callback.message.delete()
        await callback.message.answer(
            f'🛍️ <b>سفارشات در انتظار</b>\n\n'
            f'ℹ️ در حال حاضر هیچ سفارش در انتظاری وجود ندارد.',
            parse_mode="HTML",
            reply_markup=get_back_to_admin_panel_buttons()
        )
        await callback.answer()
        return
    
    user_count_names = {1: "تک کاربره", 2: "دو کاربره", 3: "سه کاربره"}
    
    for order in orders:
        user_count = order["user_count"] if order["user_count"] is not None else 1
        
        order_text = (
            f'🛍️ <b>سفارش #{order["id"]}</b>\n\n'
            f'👤 کاربر: {order["first_name"]}\n'
            f'🟣 یوزرنیم: @{order["username"] or "ندارد"}\n'
            f'🔝 آیدی: <code>{order["user_id"]}</code>\n'
            f'💎 {"─" * 15}\n'
            f'🔗 سرور: <b>{order["server"]}</b>\n'
            f'🔝 حجم: <b>{order["volume"]}</b> گیگ\n'
            f'⏰ مدت: <b>{order["duration"]}</b> روز\n'
            f'👤 تعداد کاربر: <b>{user_count_names.get(user_count, "تک کاربره")}</b>\n'
            f'🥇 مبلغ: <b>{order["total_price"]:,}</b> تومان\n'
            f'⏰ تاریخ: {order["created_at"][:16]}\n\n'
            f'🖱 برای تایید و ارسال کانفیگ، از دکمه زیر استفاده کن'
        )
        
        await callback.message.answer(
            order_text,
            parse_mode="HTML",
            reply_markup=get_admin_order_buttons(order["id"])
        )
    
    await callback.message.delete()
    await callback.answer()


def get_admin_order_buttons(order_id):
    buttons = [
        [
            InlineKeyboardButton(text="✅ تایید و ارسال کانفیگ", callback_data=f"approve_order_{order_id}", style="success"),
            InlineKeyboardButton(text="❌ رد سفارش", callback_data=f"reject_order_{order_id}", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==================== 14. تایید/رد سفارش ====================
@router.callback_query(F.data.startswith("approve_order_"))
async def admin_approve_order(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[2])
    temp_admin_data["current_order_id"] = order_id
    
    await callback.message.delete()
    await callback.message.answer(
        f'✅ <b>تایید سفارش #{order_id}</b>\n\n'
        f'🖱 اطلاعات کانفیگ سرور رو برام بفرست:\n'
        f'‼️ (متن، لینک، فایل - هر چی هست)\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_order_config)
    await callback.answer()


@router.message(AdminStates.waiting_for_order_config)
async def send_config_to_user(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        if "current_order_id" in temp_admin_data:
            del temp_admin_data["current_order_id"]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    order_id = temp_admin_data.get("current_order_id")
    if not order_id:
        await message.answer(
            f'🚨 <b>خطا! لطفاً دوباره از پنل ادمین اقدام کن.</b>',
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    
    if not order:
        await message.answer(
            f'🚨 <b>سفارش #{order_id} یافت نشد!</b>',
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    user_id = order["user_id"]
    
    cursor.execute("UPDATE orders SET status = 'completed', config_info = ? WHERE id = ?", 
                   ("ارسال شده", order_id))
    conn.commit()
    conn.close()
    
    if message.text:
        await bot.send_message(
            user_id,
            f'🤎 <b>سفارش شما تایید شد!</b>\n\n'
            f'🔗 <b>اطلاعات سرویس شما:</b>\n\n'
            f'<code>{message.text}</code>\n\n'
            f'🟫 از خرید شما متشکریم! 🌟\n\n'
            f'🖱 برای کپی کردن، روی متن بالا کلیک کن و نگه دار.',
            parse_mode="HTML"
        )
    elif message.document:
        await bot.send_document(
            user_id,
            message.document.file_id,
            caption=f'🤎 <b>سفارش شما تایید شد!</b>\n\n'
                    f'🔗 فایل کانفیگ شما دریافت کن.',
            parse_mode="HTML"
        )
    elif message.photo:
        await bot.send_photo(
            user_id,
            message.photo[-1].file_id,
            caption=f'🤎 <b>سفارش شما تایید شد!</b>\n\n'
                    f'🔗 تصویر کانفیگ شما.',
            parse_mode="HTML"
        )
    else:
        await message.answer(
            f'🚨 <b>قالب پیام پشتیبانی نمیشه!</b>\n\n'
            f'🖱 فقط متن، عکس یا فایل.',
            parse_mode="HTML"
        )
        return
    
    await message.answer(
        f'✅ <b>کانفیگ سفارش #{order_id} با موفقیت برای کاربر ارسال شد!</b>',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.clear()
    if "current_order_id" in temp_admin_data:
        del temp_admin_data["current_order_id"]


@router.callback_query(F.data.startswith("reject_order_"))
async def admin_reject_order(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[2])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, total_price FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()
    
    if order:
        user_id = order["user_id"]
        current_balance = User.get_balance(user_id)
        new_balance = current_balance + order["total_price"]
        User.update_balance(user_id, new_balance)
        
        cursor.execute("UPDATE orders SET status = 'rejected' WHERE id = ?", (order_id,))
        conn.commit()
        
        await bot.send_message(
            user_id,
            f'💀 <b>سفارش شما رد شد!</b>\n\n'
            f'🥇 مبلغ {order["total_price"]:,} تومان به کیف پول شما برگشت داده شد.\n'
            f'💳 موجودی جدید: {new_balance:,} تومان\n\n'
            f'💻 در صورت نیاز با پشتیبانی تماس بگیرید.',
            parse_mode="HTML"
        )
    
    conn.close()
    
    await callback.message.delete()
    await callback.message.answer(
        f'✅ <b>سفارش #{order_id} رد شد و وجه برگشت داده شد.</b>',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await callback.answer()


# ==================== 15. مشاهده واریزی‌ها ====================
@router.callback_query(F.data == "admin_view_transactions")
async def admin_view_transactions(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, u.first_name, u.username 
        FROM transactions t
        JOIN users u ON t.user_id = u.user_id
        WHERE t.status = 'pending'
        ORDER BY t.id DESC
    """)
    transactions = cursor.fetchall()
    conn.close()
    
    if not transactions:
        await callback.message.delete()
        await callback.message.answer(
            f'💸 <b>واریزی‌های در انتظار</b>\n\n'
            f'ℹ️ در حال حاضر هیچ درخواست واریزی در انتظاری وجود ندارد.',
            parse_mode="HTML",
            reply_markup=get_back_to_admin_panel_buttons()
        )
        await callback.answer()
        return
    
    for trans in transactions:
        currency_text = "💳 ریالی" if trans["currency_type"] == "rial" else f"💎 ارزی ({trans['crypto_currency']})"
        
        trans_text = (
            f'💸 <b>درخواست #{trans["id"]}</b>\n\n'
            f'👤 کاربر: {trans["first_name"]}\n'
            f'🟣 یوزرنیم: @{trans["username"] or "ندارد"}\n'
            f'🔝 آیدی: <code>{trans["user_id"]}</code>\n'
            f'💎 {"─" * 15}\n'
            f'🥇 نوع: {currency_text}\n'
            f'💸 مبلغ: <b>{trans["amount"]:,}</b> تومان\n'
        )
        
        if trans["crypto_amount"]:
            trans_text += f'💎 مقدار ارز: <b>{trans["crypto_amount"]:.2f}</b>\n'
        
        trans_text += (
            f'⏰ تاریخ: {trans["created_at"][:16]}\n\n'
            f'🖱 برای تایید یا رد از دکمه‌ها استفاده کن'
        )
        
        await callback.message.answer(
            trans_text,
            parse_mode="HTML",
            reply_markup=get_admin_transaction_buttons(trans["id"])
        )
    
    await callback.message.delete()
    await callback.answer()


def get_admin_transaction_buttons(transaction_id):
    buttons = [
        [
            InlineKeyboardButton(text="✅ تایید واریز", callback_data=f"approve_transaction_{transaction_id}", style="success"),
            InlineKeyboardButton(text="❌ رد واریز", callback_data=f"reject_transaction_{transaction_id}", style="danger")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ==================== 16. تایید/رد واریزی ====================
@router.callback_query(F.data.startswith("approve_transaction_"))
async def admin_approve_transaction(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    transaction_id = int(callback.data.split("_")[2])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, amount FROM transactions WHERE id = ?", (transaction_id,))
    transaction = cursor.fetchone()
    
    if not transaction:
        await callback.answer('🚨 تراکنش یافت نشد!', show_alert=True)
        return
    
    user_id = transaction["user_id"]
    amount = transaction["amount"]
    
    current_balance = User.get_balance(user_id)
    new_balance = current_balance + amount
    User.update_balance(user_id, new_balance)
    
    cursor.execute("UPDATE transactions SET status = 'approved' WHERE id = ?", (transaction_id,))
    cursor.execute("INSERT INTO admin_logs (admin_id, action, target_user_id, details) VALUES (?, 'approve_deposit', ?, ?)",
                   (ADMIN_ID, user_id, f"واریز {amount:,} تومانی تایید شد"))
    conn.commit()
    conn.close()
    
    await bot.send_message(
        user_id,
        f'✅ <b>واریز شما تایید شد!</b>\n\n'
        f'💸 مبلغ <b>{amount:,}</b> تومان به کیف پول شما اضافه شد.\n'
        f'💳 موجودی جدید: <b>{new_balance:,}</b> تومان\n\n'
        f'🤎 ممنون از اعتماد شما! 🌟',
        parse_mode="HTML"
    )
    
    await callback.message.delete()
    await callback.message.answer(
        f'✅ <b>واریزی #{transaction_id} تایید شد!</b>\n\n'
        f'🥇 {amount:,} تومان به حساب کاربر اضافه شد.',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("reject_transaction_"))
async def admin_reject_transaction(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    transaction_id = int(callback.data.split("_")[2])
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, amount FROM transactions WHERE id = ?", (transaction_id,))
    transaction = cursor.fetchone()
    
    if transaction:
        cursor.execute("UPDATE transactions SET status = 'rejected' WHERE id = ?", (transaction_id,))
        conn.commit()
        
        await bot.send_message(
            transaction["user_id"],
            f'💀 <b>واریز شما رد شد!</b>\n\n'
            f'💸 مبلغ {transaction["amount"]:,} تومان\n\n'
            f'‼️ دلیل: اطلاعات واریز نامعتبر یا مشکل در تراکنش.\n'
            f'🖱 در صورت نیاز مجدداً اقدام کن یا با پشتیبانی تماس بگیر.',
            parse_mode="HTML"
        )
    
    conn.close()
    
    await callback.message.delete()
    await callback.message.answer(
        f'💀 <b>واریزی #{transaction_id} رد شد.</b>',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await callback.answer()


# ==================== 17. تغییر نرخ ارز ====================
@router.callback_query(F.data == "admin_change_rates")
async def admin_change_rates(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    current_tether = get_setting("tether_rate") or "0"
    current_tron = get_setting("tron_rate") or "0"
    
    await callback.message.delete()
    await callback.message.answer(
        f'⚡ <b>تغییر نرخ ارزها</b>\n\n'
        f'🪙 نرخ فعلی تتر (USDT): <b>{int(current_tether):,}</b> تومان\n'
        f'🪙 نرخ فعلی ترون (TRX): <b>{int(current_tron):,}</b> تومان\n\n'
        f'🖱 نرخ جدید تتر رو وارد کن:\n'
        f'‼️ مثال: 65000\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_new_tether_rate)
    await callback.answer()


@router.message(AdminStates.waiting_for_new_tether_rate)
async def set_new_tether_rate(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    try:
        rate = int(message.text.strip().replace(",", "").replace(" ", ""))
        if rate <= 0:
            raise ValueError
    except ValueError:
        await message.answer(
            f'🚨 <b>لطفاً یک عدد معتبر وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    set_setting("tether_rate", str(rate))
    
    await message.answer(
        f'✅ <b>نرخ تتر به {rate:,} تومان تغییر کرد!</b>\n\n'
        f'🖱 حالا نرخ جدید ترون رو وارد کن:\n'
        f'‼️ مثال: 8000\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_new_tron_rate)


@router.message(AdminStates.waiting_for_new_tron_rate)
async def set_new_tron_rate(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    try:
        rate = int(message.text.strip().replace(",", "").replace(" ", ""))
        if rate <= 0:
            raise ValueError
    except ValueError:
        await message.answer(
            f'🚨 <b>لطفاً یک عدد معتبر وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    set_setting("tron_rate", str(rate))
    
    await message.answer(
        f'✅ <b>نرخ ترون به {rate:,} تومان تغییر کرد!</b>\n\n'
        f'🤎 نرخ‌های ارز با موفقیت به‌روزرسانی شد!',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.clear()


# ==================== 18. تغییر ولت و کارت ====================
@router.callback_query(F.data == "admin_change_wallets")
async def admin_change_wallets(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    current_tether_wallet = get_setting("admin_wallet_tether") or "تنظیم نشده"
    current_tron_wallet = get_setting("admin_wallet_tron") or "تنظیم نشده"
    current_card = get_setting("admin_card_number") or "تنظیم نشده"
    
    await callback.message.delete()
    await callback.message.answer(
        f'💳 <b>تغییر اطلاعات مالی</b>\n\n'
        f'🪙 ولت تتر فعلی:\n<code>{current_tether_wallet}</code>\n\n'
        f'🪙 ولت ترون فعلی:\n<code>{current_tron_wallet}</code>\n\n'
        f'💎 شماره کارت فعلی:\n<code>{current_card}</code>\n\n'
        f'🖱 ولت جدید تتر (TRC20) رو وارد کن:\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_new_tether_wallet)
    await callback.answer()


@router.message(AdminStates.waiting_for_new_tether_wallet)
async def set_new_tether_wallet(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    wallet = message.text.strip()
    if len(wallet) < 10:
        await message.answer(
            f'🚨 <b>لطفاً یک آدرس ولت معتبر وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    set_setting("admin_wallet_tether", wallet)
    
    await message.answer(
        f'✅ <b>ولت تتر به‌روزرسانی شد!</b>\n'
        f'<code>{wallet}</code>\n\n'
        f'🖱 حالا ولت جدید ترون (TRC20) رو وارد کن:\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_new_tron_wallet)


@router.message(AdminStates.waiting_for_new_tron_wallet)
async def set_new_tron_wallet(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    wallet = message.text.strip()
    if len(wallet) < 10:
        await message.answer(
            f'🚨 <b>لطفاً یک آدرس ولت معتبر وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    set_setting("admin_wallet_tron", wallet)
    
    await message.answer(
        f'✅ <b>ولت ترون به‌روزرسانی شد!</b>\n'
        f'<code>{wallet}</code>\n\n'
        f'🖱 حالا شماره کارت جدید رو وارد کن:\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_new_card)


@router.message(AdminStates.waiting_for_new_card)
async def set_new_card(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    card = message.text.strip()
    if len(card) < 16:
        await message.answer(
            f'🚨 <b>لطفاً یک شماره کارت ۱۶ رقمی معتبر وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    set_setting("admin_card_number", card)
    
    await message.answer(
        f'✅ <b>شماره کارت به‌روزرسانی شد!</b>\n'
        f'<code>{card}</code>\n\n'
        f'🤎 تمام اطلاعات مالی با موفقیت به‌روزرسانی شد!',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.clear()


# ==================== 19. مدیریت محصولات ====================
@router.callback_query(F.data == "admin_manage_products")
async def admin_manage_products(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'🔗 <b>مدیریت محصولات (سرورها)</b>\n\n'
        f'🖱 از منوی زیر میتونی:\n'
        f'✅ محصول جدید اضافه کنی\n'
        f'🔝 محصولات موجود رو ببینی\n'
        f'✏️ محصولات رو ویرایش یا حذف کنی\n\n'
        f'🖱 لطفاً یکی از گزینه‌ها رو انتخاب کن:',
        parse_mode="HTML",
        reply_markup=get_product_management_buttons()
    )
    await callback.answer()


def get_product_management_buttons():
    buttons = [
        [InlineKeyboardButton(text="➕ افزودن محصول جدید", callback_data="admin_add_product", style="success")],
        [InlineKeyboardButton(text="📋 لیست محصولات", callback_data="admin_list_products", style="primary")],
        [InlineKeyboardButton(text="🔙 بازگشت به پنل ادمین", callback_data="back_to_admin_panel", style="danger")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_list_buttons(products):
    buttons = []
    for product in products:
        status_text = "فعال" if product["is_active"] else "غیرفعال"
        buttons.append([InlineKeyboardButton(
            text=f"{product['name']} - {product['price_per_gb']:,} تومان/گیگ ({status_text})",
            callback_data=f"product_edit_{product['id']}",
            style="primary"
        )])
    buttons.append([InlineKeyboardButton(
        text="🔙 بازگشت به مدیریت محصولات",
        callback_data="admin_manage_products",
        style="danger"
    )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_action_buttons(product_id):
    buttons = [
        [InlineKeyboardButton(text="✏️ ویرایش محصول", callback_data=f"product_edit_form_{product_id}", style="primary")],
        [InlineKeyboardButton(text="🗑️ حذف محصول", callback_data=f"product_delete_{product_id}", style="danger")],
        [InlineKeyboardButton(text="🔄 تغییر وضعیت", callback_data=f"product_toggle_{product_id}", style="primary")],
        [InlineKeyboardButton(text="🔙 بازگشت به لیست محصولات", callback_data="admin_list_products", style="danger")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_color_buttons():
    buttons = [
        [
            InlineKeyboardButton(text="🔴 قرمز", callback_data="color_danger", style="danger"),
            InlineKeyboardButton(text="🔵 آبی", callback_data="color_primary", style="primary")
        ],
        [InlineKeyboardButton(text="🟢 سبز", callback_data="color_success", style="success")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "admin_add_product")
async def admin_add_product_start(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'➕ <b>افزودن محصول جدید</b>\n\n'
        f'🖱 نام سرور رو وارد کن:\n'
        f'‼️ مثال: آلمان, آمریکا, انگلیس, کانادا, هلند\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_product_name)
    await callback.answer()


@router.message(AdminStates.waiting_for_product_name)
async def get_product_name(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    name = message.text.strip()
    if len(name) < 2:
        await message.answer(
            f'🚨 <b>نام سرور باید حداقل 2 کاراکتر باشه!</b>\n\n'
            f'🖱 لطفاً دوباره وارد کن:',
            parse_mode="HTML"
        )
        return
    
    temp_admin_data["new_product_name"] = name
    
    await message.answer(
        f'✅ <b>نام سرور: {name}</b>\n\n'
        f'🥇 قیمت هر گیگ رو به تومان وارد کن:\n'
        f'‼️ مثال: 18000, 8000, 15000\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_product_price)


@router.message(AdminStates.waiting_for_product_price)
async def get_product_price(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    try:
        price = int(message.text.strip().replace(",", "").replace(" ", ""))
        if price <= 0:
            raise ValueError
        if price > 1000000:
            await message.answer(
                f'🚨 <b>قیمت هر گیگ نباید بیشتر از ۱,۰۰۰,۰۰۰ تومان باشه!</b>\n\n'
                f'🖱 لطفاً دوباره وارد کن:',
                parse_mode="HTML"
            )
            return
    except ValueError:
        await message.answer(
            f'🚨 <b>لطفاً یک عدد معتبر وارد کن!</b>\n\n'
            f'🖱 مثال: 18000, 8000, 15000',
            parse_mode="HTML"
        )
        return
    
    temp_admin_data["new_product_price"] = price
    
    await message.answer(
        f'✅ <b>نام سرور:</b> {temp_admin_data["new_product_name"]}\n'
        f'🥇 <b>قیمت هر گیگ:</b> {price:,} تومان\n\n'
        f'🎨 <b>رنگ دکمه رو انتخاب کن:</b>',
        parse_mode="HTML",
        reply_markup=get_color_buttons()
    )
    await state.set_state(AdminStates.waiting_for_product_color)


@router.callback_query(AdminStates.waiting_for_product_color)
async def get_product_color(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    color = callback.data.split("_")[1]
    color_names = {"danger": "🔴 قرمز", "primary": "🔵 آبی", "success": "🟢 سبز"}
    
    name = temp_admin_data["new_product_name"]
    price = temp_admin_data["new_product_price"]
    
    Product.create(name, price, color)
    
    await callback.message.delete()
    await callback.message.answer(
        f'✅ <b>محصول جدید با موفقیت اضافه شد!</b>\n\n'
        f'🔗 نام سرور: <b>{name}</b>\n'
        f'🥇 قیمت هر گیگ: <b>{price:,}</b> تومان\n'
        f'🎨 رنگ دکمه: {color_names[color]}\n\n'
        f'🖱 از منوی مدیریت محصولات استفاده کن:',
        parse_mode="HTML",
        reply_markup=get_product_management_buttons()
    )
    
    del temp_admin_data["new_product_name"]
    del temp_admin_data["new_product_price"]
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "admin_list_products")
async def admin_list_products(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    products = Product.get_all()
    
    if not products:
        await callback.message.delete()
        await callback.message.answer(
            f'📋 <b>لیست محصولات</b>\n\n'
            f'ℹ️ هیچ محصولی یافت نشد!\n'
            f'🖱 از منوی مدیریت محصولات، محصول جدید اضافه کن.',
            parse_mode="HTML",
            reply_markup=get_product_management_buttons()
        )
        await callback.answer()
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'📋 <b>لیست محصولات (سرورها)</b>\n\n'
        f'🖱 روی هر محصول کلیک کن تا عملیات ویرایش/حذف رو انجام بدی:\n\n'
        f'✅ = فعال | ❌ = غیرفعال',
        parse_mode="HTML",
        reply_markup=get_product_list_buttons(products)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("product_edit_"))
async def product_action_menu(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    if callback.data.startswith("product_edit_form_"):
        await product_edit_form(callback, state)
        return
    
    try:
        product_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("❌ خطا در شناسایی محصول!", show_alert=True)
        return
    
    product = Product.get_by_id(product_id)
    
    if not product:
        await callback.answer('🚨 محصول یافت نشد!', show_alert=True)
        return
    
    status_text = "✅ فعال" if product["is_active"] else "❌ غیرفعال"
    color_names = {"danger": "🔴 قرمز", "primary": "🔵 آبی", "success": "🟢 سبز"}
    
    await callback.message.delete()
    await callback.message.answer(
        f'🛒 <b>اطلاعات محصول</b>\n\n'
        f'🔝 شناسه: <b>{product["id"]}</b>\n'
        f'🌎 نام سرور: <b>{product["name"]}</b>\n'
        f'🥇 قیمت هر گیگ: <b>{product["price_per_gb"]:,}</b> تومان\n'
        f'🎨 رنگ دکمه: {color_names.get(product["button_color"], "🔵 آبی")}\n'
        f'🚩 وضعیت: {status_text}\n\n'
        f'🖱 عملیات مورد نظر رو انتخاب کن:',
        parse_mode="HTML",
        reply_markup=get_product_action_buttons(product_id)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("product_edit_form_"))
async def product_edit_form(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    try:
        product_id = int(callback.data.split("_")[3])
    except (ValueError, IndexError):
        await callback.answer("❌ خطا در شناسایی محصول!", show_alert=True)
        return
    
    product = Product.get_by_id(product_id)
    
    if not product:
        await callback.answer('🚨 محصول یافت نشد!', show_alert=True)
        return
    
    temp_admin_data["editing_product_id"] = product_id
    
    await callback.message.delete()
    await callback.message.answer(
        f'✏️ <b>ویرایش محصول</b>\n\n'
        f'🌎 نام فعلی: <b>{product["name"]}</b>\n\n'
        f'🖱 نام جدید رو وارد کن (یا <code>/skip</code> برای رد شدن):',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_edit_product_name)
    await callback.answer()


@router.message(AdminStates.waiting_for_edit_product_name)
async def edit_product_name(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        if "editing_product_id" in temp_admin_data:
            del temp_admin_data["editing_product_id"]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    product_id = temp_admin_data.get("editing_product_id")
    if not product_id:
        await message.answer(
            f'🚨 <b>خطا! لطفاً دوباره تلاش کن.</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    product = Product.get_by_id(product_id)
    if not product:
        await message.answer(
            f'🚨 <b>محصول یافت نشد!</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    if message.text == "/skip":
        temp_admin_data["edit_product_name"] = product["name"]
    else:
        name = message.text.strip()
        if len(name) < 2:
            await message.answer(
                f'🚨 <b>نام باید حداقل 2 کاراکتر باشه!</b>\n\n'
                f'🖱 لطفاً دوباره وارد کن:',
                parse_mode="HTML"
            )
            return
        temp_admin_data["edit_product_name"] = name
    
    await message.answer(
        f'🥇 <b>قیمت فعلی هر گیگ:</b> {product["price_per_gb"]:,} تومان\n\n'
        f'🖱 قیمت جدید رو وارد کن (یا <code>/skip</code> برای رد شدن):',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_edit_product_price)


@router.message(AdminStates.waiting_for_edit_product_price)
async def edit_product_price(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        if "editing_product_id" in temp_admin_data:
            del temp_admin_data["editing_product_id"]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    product_id = temp_admin_data.get("editing_product_id")
    if not product_id:
        await message.answer(
            f'🚨 <b>خطا! لطفاً دوباره تلاش کن.</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    product = Product.get_by_id(product_id)
    if not product:
        await message.answer(
            f'🚨 <b>محصول یافت نشد!</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    if message.text == "/skip":
        temp_admin_data["edit_product_price"] = product["price_per_gb"]
    else:
        try:
            price = int(message.text.strip().replace(",", "").replace(" ", ""))
            if price <= 0:
                raise ValueError
            if price > 1000000:
                await message.answer(
                    f'🚨 <b>قیمت هر گیگ نباید بیشتر از ۱,۰۰۰,۰۰۰ تومان باشه!</b>\n\n'
                    f'🖱 لطفاً دوباره وارد کن:',
                    parse_mode="HTML"
                )
                return
            temp_admin_data["edit_product_price"] = price
        except ValueError:
            await message.answer(
                f'🚨 <b>لطفاً یک عدد معتبر وارد کن!</b>\n\n'
                f'🖱 مثال: 18000, 8000\n'
                f'(یا <code>/skip</code> برای رد شدن)',
                parse_mode="HTML"
            )
            return
    
    await message.answer(
        f'🎨 <b>رنگ جدید دکمه رو انتخاب کن:</b>',
        parse_mode="HTML",
        reply_markup=get_color_buttons()
    )
    await state.set_state(AdminStates.waiting_for_edit_product_color)


@router.callback_query(AdminStates.waiting_for_edit_product_color)
async def edit_product_color(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    color = callback.data.split("_")[1]
    product_id = temp_admin_data.get("editing_product_id")
    
    if not product_id:
        await callback.message.answer(
            f'🚨 <b>خطا! لطفاً دوباره تلاش کن.</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    name = temp_admin_data.get("edit_product_name")
    price = temp_admin_data.get("edit_product_price")
    
    if not name or not price:
        await callback.message.answer(
            f'🚨 <b>اطلاعات محصول کامل نیست!</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    product = Product.get_by_id(product_id)
    if not product:
        await callback.message.answer(
            f'🚨 <b>محصول یافت نشد!</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    Product.update(product_id, name, price, color, product["is_active"])
    
    color_names = {"danger": "🔴 قرمز", "primary": "🔵 آبی", "success": "🟢 سبز"}
    
    await callback.message.delete()
    await callback.message.answer(
        f'✅ <b>محصول با موفقیت ویرایش شد!</b>\n\n'
        f'🌎 نام سرور: <b>{name}</b>\n'
        f'🥇 قیمت هر گیگ: <b>{price:,}</b> تومان\n'
        f'🎨 رنگ دکمه: {color_names[color]}\n\n'
        f'🖱 از منوی مدیریت محصولات استفاده کن:',
        parse_mode="HTML",
        reply_markup=get_product_management_buttons()
    )
    
    temp_admin_data.pop("editing_product_id", None)
    temp_admin_data.pop("edit_product_name", None)
    temp_admin_data.pop("edit_product_price", None)
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.startswith("product_delete_"))
async def product_delete(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    try:
        product_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("❌ خطا در شناسایی محصول!", show_alert=True)
        return
    
    product = Product.get_by_id(product_id)
    
    if not product:
        await callback.answer('🚨 محصول یافت نشد!', show_alert=True)
        return
    
    Product.delete(product_id)
    
    await callback.message.delete()
    await callback.message.answer(
        f'🗑️ <b>محصول "{product["name"]}" با موفقیت حذف شد!</b>',
        parse_mode="HTML",
        reply_markup=get_product_management_buttons()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("product_toggle_"))
async def product_toggle_status(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    try:
        product_id = int(callback.data.split("_")[2])
    except (ValueError, IndexError):
        await callback.answer("❌ خطا در شناسایی محصول!", show_alert=True)
        return
    
    product = Product.get_by_id(product_id)
    
    if not product:
        await callback.answer('🚨 محصول یافت نشد!', show_alert=True)
        return
    
    new_status = 0 if product["is_active"] else 1
    Product.update(product_id, product["name"], product["price_per_gb"], product["button_color"], new_status)
    
    status_text = "✅ فعال" if new_status else "❌ غیرفعال"
    
    await callback.message.delete()
    await callback.message.answer(
        f'✅ <b>وضعیت محصول "{product["name"]}" به {status_text} تغییر کرد!</b>',
        parse_mode="HTML",
        reply_markup=get_product_management_buttons()
    )
    await callback.answer()


# ==================== 20. مدیریت گردونه شانس ====================
@router.callback_query(F.data == "admin_spin_panel")
async def admin_spin_panel(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    items = get_all_spin_items()
    total_chance = get_total_chance()
    
    text = (
        f'🎰 <b>مدیریت گردونه شانس</b>\n\n'
        f'🔝 تعداد آیتم‌ها: <b>{len(items)}</b>\n'
        f'💯 مجموع درصدها: <b>{total_chance}%</b>\n\n'
        f'🖱 از منوی زیر مدیریت کن:'
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ افزودن آیتم جدید", callback_data="admin_add_spin_item", style="success")],
        [InlineKeyboardButton(text="📋 لیست آیتم‌ها", callback_data="admin_list_spin_items", style="primary")],
        [InlineKeyboardButton(text="🔙 بازگشت به پنل ادمین", callback_data="back_to_admin_panel", style="danger")]
    ])
    
    await callback.message.delete()
    await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data == "admin_add_spin_item")
async def admin_add_spin_item_start(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'➕ <b>افزودن آیتم جدید به گردونه</b>\n\n'
        f'🖱 نام جایزه رو وارد کن:\n'
        f'❗ مثال: 🎁 ۱۰ گیگ رایگان\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_spin_item_name)
    await callback.answer()


@router.message(AdminStates.waiting_for_spin_item_name)
async def get_spin_item_name(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    name = message.text.strip()
    if len(name) < 2:
        await message.answer(
            f'🚨 <b>نام باید حداقل ۲ کاراکتر باشه!</b>\n\n'
            f'🖱 لطفاً دوباره وارد کن:',
            parse_mode="HTML"
        )
        return
    
    temp_admin_data["spin_item_name"] = name
    
    await message.answer(
        f'✅ <b>نام جایزه: {name}</b>\n\n'
        f'💯 درصد شانس این جایزه رو وارد کن (۱ تا ۱۰۰):\n'
        f'❗ مثال: 20\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_spin_item_chance)


@router.message(AdminStates.waiting_for_spin_item_chance)
async def get_spin_item_chance(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        if "spin_item_name" in temp_admin_data:
            del temp_admin_data["spin_item_name"]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    try:
        chance = int(message.text.strip().replace("%", ""))
        if chance < 1 or chance > 100:
            raise ValueError
    except ValueError:
        await message.answer(
            f'🚨 <b>لطفاً یک عدد بین ۱ تا ۱۰۰ وارد کن!</b>\n\n'
            f'🖱 مثال: 20\n\n'
            f'📤 برای لغو، از دکمه زیر استفاده کن',
            parse_mode="HTML"
        )
        return
    
    temp_admin_data["spin_item_chance"] = chance
    
    await message.answer(
        f'✅ <b>درصد شانس: {chance}%</b>\n\n'
        f'ℹ️ توضیحات جایزه رو وارد کن:\n'
        f'❗ مثال: ۱۰ گیگ کانفیگ رایگان از سرور آلمان\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_spin_item_description)


@router.message(AdminStates.waiting_for_spin_item_description)
async def get_spin_item_description(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        if "spin_item_name" in temp_admin_data:
            del temp_admin_data["spin_item_name"]
        if "spin_item_chance" in temp_admin_data:
            del temp_admin_data["spin_item_chance"]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    description = message.text.strip()
    if len(description) < 3:
        await message.answer(
            f'🚨 <b>توضیحات باید حداقل ۳ کاراکتر باشه!</b>\n\n'
            f'🖱 لطفاً دوباره وارد کن:',
            parse_mode="HTML"
        )
        return
    
    name = temp_admin_data.get("spin_item_name")
    chance = temp_admin_data.get("spin_item_chance")
    
    if not name or not chance:
        await message.answer(
            f'🚨 <b>خطا! لطفاً دوباره از اول شروع کن.</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    item_id = add_spin_item(name, chance, description)
    
    del temp_admin_data["spin_item_name"]
    del temp_admin_data["spin_item_chance"]
    
    await message.answer(
        f'✅ <b>آیتم با موفقیت اضافه شد!</b>\n\n'
        f'🎁 نام: <b>{name}</b>\n'
        f'💯 شانس: <b>{chance}%</b>\n'
        f'ℹ️ توضیحات: {description}\n'
        f'🔝 شناسه: <b>{item_id}</b>\n\n'
        f'🖱 از منوی مدیریت گردونه استفاده کن:',
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎰 بازگشت به مدیریت گردونه", callback_data="admin_spin_panel", style="primary")]
        ])
    )
    await state.clear()


@router.callback_query(F.data == "admin_list_spin_items")
async def admin_list_spin_items(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    items = get_all_spin_items()
    
    if not items:
        await callback.message.delete()
        await callback.message.answer(
            f'ℹ️ <b>هیچ آیتمی در گردونه وجود ندارد!</b>\n\n'
            f'🖱 از دکمه <b>افزودن آیتم جدید</b> استفاده کن.',
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➕ افزودن آیتم جدید", callback_data="admin_add_spin_item", style="success")],
                [InlineKeyboardButton(text="🔙 بازگشت به مدیریت گردونه", callback_data="admin_spin_panel", style="danger")]
            ])
        )
        await callback.answer()
        return
    
    buttons = []
    for item in items:
        status_text = "✅ فعال" if item["is_active"] else "❌ غیرفعال"
        buttons.append([InlineKeyboardButton(
            text=f"{item['name']} - {item['chance']}% ({status_text})",
            callback_data=f"spin_item_edit_{item['id']}",
            style="primary"
        )])
    
    buttons.append([InlineKeyboardButton(text="➕ افزودن آیتم جدید", callback_data="admin_add_spin_item", style="success")])
    buttons.append([InlineKeyboardButton(text="🔙 بازگشت به مدیریت گردونه", callback_data="admin_spin_panel", style="danger")])
    
    await callback.message.delete()
    await callback.message.answer(
        f'📋 <b>لیست آیتم‌های گردونه</b>\n\n'
        f'🖱 روی هر آیتم کلیک کن تا ویرایش یا حذف کنی:',
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("spin_item_edit_form_"))
async def spin_item_edit_form(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    try:
        item_id = int(callback.data.split("_")[4])
    except (ValueError, IndexError):
        await callback.answer('🚨 خطا در شناسایی آیتم!', show_alert=True)
        return
    
    item = get_spin_item_by_id(item_id)
    
    if not item:
        await callback.answer('🚨 آیتم یافت نشد!', show_alert=True)
        return
    
    temp_admin_data["editing_spin_item_id"] = item_id
    
    await callback.message.delete()
    await callback.message.answer(
        f'✏️ <b>ویرایش آیتم گردونه</b>\n\n'
        f'⭐ نام فعلی: <b>{item["name"]}</b>\n\n'
        f'🖱 نام جدید رو وارد کن (یا <code>/skip</code> برای رد شدن):',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_edit_spin_item_name)
    await callback.answer()


@router.callback_query(F.data.startswith("spin_item_edit_"))
async def spin_item_edit_menu(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    if "_form_" in callback.data:
        return
    
    try:
        item_id = int(callback.data.split("_")[3])
    except (ValueError, IndexError):
        await callback.answer('🚨 خطا در شناسایی آیتم!', show_alert=True)
        return
    
    item = get_spin_item_by_id(item_id)
    
    if not item:
        await callback.answer('🚨 آیتم یافت نشد!', show_alert=True)
        return
    
    status_text = "✅ فعال" if item["is_active"] else "❌ غیرفعال"
    
    text = (
        f'🎁 <b>مدیریت آیتم</b>\n\n'
        f'🔝 شناسه: <b>{item["id"]}</b>\n'
        f'⭐ نام: <b>{item["name"]}</b>\n'
        f'💯 درصد شانس: <b>{item["chance"]}%</b>\n'
        f'ℹ️ توضیحات: {item["description"]}\n'
        f'🚩 وضعیت: {status_text}\n\n'
        f'🖱 عملیات مورد نظر رو انتخاب کن:'
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ ویرایش", callback_data=f"spin_item_edit_form_{item_id}", style="primary")],
        [InlineKeyboardButton(text="🔄 تغییر وضعیت", callback_data=f"spin_item_toggle_{item_id}", style="primary")],
        [InlineKeyboardButton(text="🗑️ حذف آیتم", callback_data=f"spin_item_delete_{item_id}", style="danger")],
        [InlineKeyboardButton(text="🔙 بازگشت به لیست", callback_data="admin_list_spin_items", style="danger")]
    ])
    
    await callback.message.delete()
    await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.message(AdminStates.waiting_for_edit_spin_item_name)
async def edit_spin_item_name(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        if "editing_spin_item_id" in temp_admin_data:
            del temp_admin_data["editing_spin_item_id"]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    item_id = temp_admin_data.get("editing_spin_item_id")
    if not item_id:
        await message.answer(
            f'🚨 <b>خطا! لطفاً دوباره تلاش کن.</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    item = get_spin_item_by_id(item_id)
    if not item:
        await message.answer(
            f'🚨 <b>آیتم یافت نشد!</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    if message.text == "/skip":
        temp_admin_data["edit_spin_item_name"] = item["name"]
    else:
        name = message.text.strip()
        if len(name) < 2:
            await message.answer(
                f'🚨 <b>نام باید حداقل ۲ کاراکتر باشه!</b>\n\n'
                f'🖱 لطفاً دوباره وارد کن:',
                parse_mode="HTML"
            )
            return
        temp_admin_data["edit_spin_item_name"] = name
    
    await message.answer(
        f'💯 <b>درصد شانس فعلی:</b> {item["chance"]}%\n\n'
        f'🖱 درصد جدید رو وارد کن (یا <code>/skip</code> برای رد شدن):',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_edit_spin_item_chance)


@router.message(AdminStates.waiting_for_edit_spin_item_chance)
async def edit_spin_item_chance(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        if "editing_spin_item_id" in temp_admin_data:
            del temp_admin_data["editing_spin_item_id"]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    item_id = temp_admin_data.get("editing_spin_item_id")
    if not item_id:
        await message.answer(
            f'🚨 <b>خطا! لطفاً دوباره تلاش کن.</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    item = get_spin_item_by_id(item_id)
    if not item:
        await message.answer(
            f'🚨 <b>آیتم یافت نشد!</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    if message.text == "/skip":
        temp_admin_data["edit_spin_item_chance"] = item["chance"]
    else:
        try:
            chance = int(message.text.strip().replace("%", ""))
            if chance < 1 or chance > 100:
                raise ValueError
            temp_admin_data["edit_spin_item_chance"] = chance
        except ValueError:
            await message.answer(
                f'🚨 <b>لطفاً یک عدد بین ۱ تا ۱۰۰ وارد کن!</b>\n\n'
                f'🖱 مثال: 20\n\n'
                f'📤 برای لغو، از دکمه زیر استفاده کن',
                parse_mode="HTML"
            )
            return
    
    await message.answer(
        f'ℹ️ <b>توضیحات فعلی:</b> {item["description"]}\n\n'
        f'🖱 توضیحات جدید رو وارد کن (یا <code>/skip</code> برای رد شدن):',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_edit_spin_item_description)


@router.message(AdminStates.waiting_for_edit_spin_item_description)
async def edit_spin_item_description(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        if "editing_spin_item_id" in temp_admin_data:
            del temp_admin_data["editing_spin_item_id"]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    item_id = temp_admin_data.get("editing_spin_item_id")
    if not item_id:
        await message.answer(
            f'🚨 <b>خطا! لطفاً دوباره تلاش کن.</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    item = get_spin_item_by_id(item_id)
    if not item:
        await message.answer(
            f'🚨 <b>آیتم یافت نشد!</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    if message.text == "/skip":
        description = item["description"]
    else:
        description = message.text.strip()
        if len(description) < 3:
            await message.answer(
                f'🚨 <b>توضیحات باید حداقل ۳ کاراکتر باشه!</b>\n\n'
                f'🖱 لطفاً دوباره وارد کن:',
                parse_mode="HTML"
            )
            return
    
    name = temp_admin_data.get("edit_spin_item_name", item["name"])
    chance = temp_admin_data.get("edit_spin_item_chance", item["chance"])
    
    update_spin_item(item_id, name, chance, description, item["is_active"])
    
    await message.answer(
        f'✅ <b>آیتم با موفقیت ویرایش شد!</b>\n\n'
        f'🎁 نام: <b>{name}</b>\n'
        f'💯 شانس: <b>{chance}%</b>\n'
        f'ℹ️ توضیحات: {description}',
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به لیست", callback_data="admin_list_spin_items", style="danger")]
        ])
    )
    
    temp_admin_data.pop("editing_spin_item_id", None)
    temp_admin_data.pop("edit_spin_item_name", None)
    temp_admin_data.pop("edit_spin_item_chance", None)
    await state.clear()


@router.callback_query(F.data.startswith("spin_item_toggle_"))
async def spin_item_toggle(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    try:
        item_id = int(callback.data.split("_")[3])
    except (ValueError, IndexError):
        await callback.answer('🚨 خطا در شناسایی آیتم!', show_alert=True)
        return
    
    toggle_spin_item_status(item_id)
    
    item = get_spin_item_by_id(item_id)
    status_text = "✅ فعال" if item["is_active"] else "❌ غیرفعال"
    
    await callback.message.delete()
    await callback.message.answer(
        f'✅ <b>وضعیت آیتم با موفقیت تغییر کرد!</b>\n\n'
        f'🎁 آیتم: <b>{item["name"]}</b>\n'
        f'🚩 وضعیت جدید: {status_text}',
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به لیست", callback_data="admin_list_spin_items", style="danger")]
        ])
    )
    await callback.answer()


@router.callback_query(F.data.startswith("spin_item_delete_"))
async def spin_item_delete(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    try:
        item_id = int(callback.data.split("_")[3])
    except (ValueError, IndexError):
        await callback.answer('🚨 خطا در شناسایی آیتم!', show_alert=True)
        return
    
    item = get_spin_item_by_id(item_id)
    
    if not item:
        await callback.answer('🚨 آیتم یافت نشد!', show_alert=True)
        return
    
    delete_spin_item(item_id)
    
    await callback.message.delete()
    await callback.message.answer(
        f'🗑️ <b>آیتم با موفقیت حذف شد!</b>\n\n'
        f'🎁 آیتم حذف شده: <b>{item["name"]}</b>',
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 بازگشت به لیست", callback_data="admin_list_spin_items", style="danger")]
        ])
    )
    await callback.answer()


# ==================== 21. مدیریت تیکت‌ها ====================
@router.callback_query(F.data == "admin_tickets_panel")
async def admin_tickets_panel(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    tickets = get_all_tickets()
    open_count = get_open_tickets_count()
    
    text = (
        f'🎫 <b>مدیریت تیکت‌های پشتیبانی</b>\n\n'
        f'📊 کل تیکت‌ها: <b>{len(tickets)}</b>\n'
        f'🟢 تیکت‌های باز: <b>{open_count}</b>\n\n'
        f'🖱 روی هر تیکت کلیک کن تا پاسخ بدی یا مدیریتش کنی:'
    )
    
    await callback.message.delete()
    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_ticket_list_buttons(tickets)
    )
    await callback.answer()


def get_admin_ticket_list_buttons(tickets):
    buttons = []
    for ticket in tickets:
        status_emoji = "🟢" if ticket["status"] == "open" else "🟡" if ticket["status"] == "answered" else "🔴"
        user_display = ticket["first_name"] or ticket["username"] or str(ticket["user_id"])
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


def get_ticket_detail_buttons(ticket_id, user_id, is_admin=False):
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
    
    buttons.append([InlineKeyboardButton(
        text="🔙 بازگشت",
        callback_data="admin_tickets_panel" if is_admin else "ticket_menu",
        style="danger"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data.startswith("admin_ticket_detail_"))
async def admin_ticket_detail(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    ticket_id = int(callback.data.split("_")[3])
    ticket = get_ticket_by_id(ticket_id)
    
    if not ticket:
        await callback.answer('🚨 تیکت یافت نشد!', show_alert=True)
        return
    
    status_emoji = "🟢" if ticket["status"] == "open" else "🟡" if ticket["status"] == "answered" else "🔴"
    status_text = "باز" if ticket["status"] == "open" else "پاسخ داده شده" if ticket["status"] == "answered" else "بسته"
    
    text = (
        f'🎫 <b>تیکت #{ticket["id"]}</b>\n\n'
        f'👤 کاربر: {ticket["first_name"] or "نامشخص"}\n'
        f'🔝 آیدی: <code>{ticket["user_id"]}</code>\n'
        f'🟣 یوزرنیم: @{ticket["username"] or "ندارد"}\n'
        f'🚩 وضعیت: {status_emoji} {status_text}\n\n'
        f'💎 {"─" * 15}\n'
        f'📤 <b>پیام کاربر:</b>\n{ticket["message"]}\n\n'
    )
    
    if ticket["admin_answer"]:
        text += f'✏️ <b>پاسخ ادمین:</b>\n{ticket["admin_answer"]}\n\n'
    
    await callback.message.delete()
    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_ticket_detail_buttons(ticket_id, ticket["user_id"], is_admin=True)
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_ticket_answer_"))
async def admin_ticket_answer_start(callback: CallbackQuery, state: FSMContext):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    ticket_id = int(callback.data.split("_")[3])
    ticket = get_ticket_by_id(ticket_id)
    
    if not ticket:
        await callback.answer('🚨 تیکت یافت نشد!', show_alert=True)
        return
    
    temp_admin_data["current_ticket_id"] = ticket_id
    
    await callback.message.delete()
    await callback.message.answer(
        f'✏️ <b>پاسخ به تیکت #{ticket_id}</b>\n\n'
        f'👤 کاربر: {ticket["first_name"] or "نامشخص"}\n'
        f'🔝 آیدی: <code>{ticket["user_id"]}</code>\n\n'
        f'📤 <b>پیام کاربر:</b>\n{ticket["message"]}\n\n'
        f'🖱 پاسخ خود را وارد کنید:\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_ticket_answer)
    await callback.answer()


@router.message(AdminStates.waiting_for_ticket_answer)
async def process_ticket_answer(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        if "current_ticket_id" in temp_admin_data:
            del temp_admin_data["current_ticket_id"]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    ticket_id = temp_admin_data.get("current_ticket_id")
    if not ticket_id:
        await message.answer(
            f'🚨 <b>خطا! لطفاً دوباره از پنل ادمین اقدام کن.</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        await message.answer(
            f'🚨 <b>تیکت یافت نشد!</b>',
            parse_mode="HTML")
        await state.clear()
        return
    
    admin_answer = message.text.strip()
    if len(admin_answer) < 3:
        await message.answer(
            f'🚨 <b>پاسخ باید حداقل ۳ کاراکتر باشه!</b>',
            parse_mode="HTML")
        return
    
    answer_ticket(ticket_id, admin_answer, ADMIN_ID)
    
    try:
        await bot.send_message(
            ticket["user_id"],
            f'🎫 <b>پاسخ به تیکت شما</b>\n\n'
            f'📤 <b>پیام شما:</b>\n{ticket["message"]}\n\n'
            f'✏️ <b>پاسخ ادمین:</b>\n{admin_answer}\n\n'
            f'❤️ اگر سوال دیگری داری، دوباره تیکت جدید ارسال کن.',
            parse_mode="HTML")
    except:
        pass
    
    await message.answer(
        f'✅ <b>پاسخ شما با موفقیت به کاربر ارسال شد!</b>\n\n'
        f'🔝 تیکت #{ticket_id} - وضعیت: پاسخ داده شده',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    
    del temp_admin_data["current_ticket_id"]
    await state.clear()


@router.callback_query(F.data.startswith("admin_ticket_close_"))
async def admin_ticket_close(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    ticket_id = int(callback.data.split("_")[3])
    ticket = get_ticket_by_id(ticket_id)
    
    if not ticket:
        await callback.answer('🚨 تیکت یافت نشد!', show_alert=True)
        return
    
    close_ticket(ticket_id)
    
    try:
        await bot.send_message(
            ticket["user_id"],
            f'🔒 <b>تیکت شما بسته شد!</b>\n\n'
            f'🎫 تیکت #{ticket_id} توسط ادمین بسته شد.\n\n'
            f'🖱 اگر سوال جدیدی داری، تیکت جدید ارسال کن.',
            parse_mode="HTML")
    except:
        pass
    
    await callback.message.delete()
    await callback.message.answer(
        f'✅ <b>تیکت #{ticket_id} با موفقیت بسته شد!</b>',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_ticket_delete_"))
async def admin_ticket_delete(callback: CallbackQuery):
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    ticket_id = int(callback.data.split("_")[3])
    ticket = get_ticket_by_id(ticket_id)
    
    if not ticket:
        await callback.answer('🚨 تیکت یافت نشد!', show_alert=True)
        return
    
    delete_ticket(ticket_id)
    
    await callback.message.delete()
    await callback.message.answer(
        f'🗑️ <b>تیکت #{ticket_id} با موفقیت حذف شد!</b>',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await callback.answer()


# ==================== برگشت به پنل ادمین ====================
@router.callback_query(F.data == "back_to_admin_panel")
async def back_to_admin_panel(callback: CallbackQuery):
    """برگشت به پنل ادمین"""
    try:
        await callback.message.delete()
    except:
        pass
    
    user_id = callback.from_user.id
    
    if not is_user_admin(user_id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    class FakeMessage:
        def __init__(self, user_id):
            self.from_user = type('obj', (object,), {'id': user_id})
            self.chat = type('obj', (object,), {'id': user_id})
        
        async def answer(self, text, parse_mode=None, reply_markup=None):
            await callback.message.answer(text, parse_mode=parse_mode, reply_markup=reply_markup)
    
    fake_message = FakeMessage(user_id)
    await admin_panel(fake_message)
    await callback.answer()

# ==================== مدیریت رفرال ====================

@router.callback_query(F.data == "admin_referral_settings")
async def admin_referral_settings(callback: CallbackQuery):
    """تنظیمات رفرال"""
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    settings = get_referral_settings()
    
    status_text = "🟢 فعال" if settings["enabled"] == "on" else "🔴 غیرفعال"
    reward_text = "💰 موجودی" if settings["reward_type"] == "balance" else "🎯 تخفیف"
    require_text = "🛒 نیاز به خرید" if settings.get("require_purchase", "on") == "on" else "⚡ فوری (بدون نیاز به خرید)"
    
    text = (
        f'🔗 <b>مدیریت سیستم رفرال</b>\n\n'
        f'📊 <b>وضعیت فعلی:</b>\n'
        f'• وضعیت: {status_text}\n'
        f'• نوع پاداش: {reward_text}\n'
        f'• مبلغ پاداش: {settings["reward_amount"]:,} تومان\n'
        f'• درصد تخفیف: {settings["discount_percent"]}%\n'
        f'• حالت دریافت پاداش: {require_text}\n'
        f'• حداقل خرید: {settings["min_purchase"]:,} تومان\n\n'
        f'🖱 از منوی زیر برای مدیریت استفاده کن:'
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"🔄 {'غیرفعال' if settings['enabled'] == 'on' else 'فعال'} کردن رفرال",
            callback_data=f"admin_ref_toggle_{'off' if settings['enabled'] == 'on' else 'on'}",
            style="danger" if settings['enabled'] == 'on' else "success"
        )],
        [InlineKeyboardButton(
            text=f"📌 حالت پاداش: {'نیاز به خرید' if settings.get('require_purchase', 'on') == 'on' else 'فوری'}",
            callback_data=f"admin_ref_require_{'off' if settings.get('require_purchase', 'on') == 'on' else 'on'}",
            style="primary"
        )],
        [InlineKeyboardButton(
            text="💰 تغییر پاداش به موجودی",
            callback_data="admin_ref_type_balance",
            style="primary"
        )],
        [InlineKeyboardButton(
            text="🎯 تغییر پاداش به تخفیف",
            callback_data="admin_ref_type_discount",
            style="primary"
        )],
        [InlineKeyboardButton(
            text="✏️ تغییر مبلغ پاداش",
            callback_data="admin_ref_amount",
            style="primary"
        )],
        [InlineKeyboardButton(
            text="✏️ تغییر درصد تخفیف",
            callback_data="admin_ref_discount",
            style="primary"
        )],
        [InlineKeyboardButton(
            text="📊 آمار رفرال‌ها",
            callback_data="admin_ref_stats",
            style="primary"
        )],
        [InlineKeyboardButton(
            text="🔙 بازگشت به پنل ادمین",
            callback_data="back_to_admin_panel",
            style="danger"
        )]
    ])
    
    await callback.message.delete()
    await callback.message.answer(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("admin_ref_toggle_"))
async def admin_ref_toggle(callback: CallbackQuery):
    """تغییر وضعیت رفرال"""
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    status = callback.data.split("_")[3]
    set_referral_setting("enabled", status)
    
    await callback.answer(f"✅ وضعیت رفرال به {'فعال' if status == 'on' else 'غیرفعال'} تغییر کرد!")
    await admin_referral_settings(callback)


@router.callback_query(F.data.startswith("admin_ref_require_"))
async def admin_ref_require_toggle(callback: CallbackQuery):
    """تغییر حالت نیاز به خرید برای دریافت پاداش"""
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    status = callback.data.split("_")[3]
    set_referral_setting("require_purchase", status)
    
    status_text = "نیاز به خرید" if status == "on" else "فوری (بدون نیاز به خرید)"
    await callback.answer(f"✅ حالت پاداش به {status_text} تغییر کرد!")
    await admin_referral_settings(callback)


@router.callback_query(F.data == "admin_ref_type_balance")
async def admin_ref_type_balance(callback: CallbackQuery):
    """تغییر نوع پاداش به موجودی"""
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    set_referral_setting("reward_type", "balance")
    await callback.answer("✅ نوع پاداش به موجودی تغییر کرد!")
    await admin_referral_settings(callback)


@router.callback_query(F.data == "admin_ref_type_discount")
async def admin_ref_type_discount(callback: CallbackQuery):
    """تغییر نوع پاداش به تخفیف"""
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    set_referral_setting("reward_type", "discount")
    await callback.answer("✅ نوع پاداش به تخفیف تغییر کرد!")
    await admin_referral_settings(callback)


@router.callback_query(F.data == "admin_ref_amount")
async def admin_ref_amount(callback: CallbackQuery, state: FSMContext):
    """تغییر مبلغ پاداش"""
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'💰 <b>تغییر مبلغ پاداش رفرال</b>\n\n'
        f'🖱 مبلغ جدید را به تومان وارد کن:\n'
        f'‼️ مثال: 10000\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_ref_amount)
    await callback.answer()


@router.message(AdminStates.waiting_for_ref_amount)
async def process_ref_amount(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    try:
        amount = int(message.text.strip().replace(",", "").replace(" ", ""))
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer(
            f'🚨 <b>لطفاً یک عدد معتبر وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    set_referral_setting("reward_amount", str(amount))
    await state.clear()
    
    await message.answer(
        f'✅ <b>مبلغ پاداش به {amount:,} تومان تغییر کرد!</b>',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )


@router.callback_query(F.data == "admin_ref_discount")
async def admin_ref_discount(callback: CallbackQuery, state: FSMContext):
    """تغییر درصد تخفیف"""
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'🎯 <b>تغییر درصد تخفیف رفرال</b>\n\n'
        f'🖱 درصد جدید را وارد کن (۱ تا ۱۰۰):\n'
        f'‼️ مثال: 15\n\n'
        f'📤 برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )
    await state.set_state(AdminStates.waiting_for_ref_discount)
    await callback.answer()


@router.message(AdminStates.waiting_for_ref_discount)
async def process_ref_discount(message: Message, state: FSMContext):
    if not is_user_admin(message.from_user.id):
        return
    
    if message.text == "🔙 بازگشت":
        await state.clear()
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    try:
        discount = int(message.text.strip().replace("%", ""))
        if discount < 1 or discount > 100:
            raise ValueError
    except ValueError:
        await message.answer(
            f'🚨 <b>لطفاً یک عدد بین ۱ تا ۱۰۰ وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    set_referral_setting("discount_percent", str(discount))
    await state.clear()
    
    await message.answer(
        f'✅ <b>درصد تخفیف به {discount}% تغییر کرد!</b>',
        parse_mode="HTML",
        reply_markup=get_back_to_admin_panel_buttons()
    )


@router.callback_query(F.data == "admin_ref_stats")
async def admin_ref_stats(callback: CallbackQuery):
    """آمار رفرال‌ها"""
    if not is_user_admin(callback.from_user.id):
        await callback.answer('💀 دسترسی ندارید!', show_alert=True)
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM referrals")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM referrals WHERE status = 'pending'")
    pending = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM referrals WHERE status = 'completed'")
    completed = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT referrer_id) FROM referrals")
    unique_referrers = cursor.fetchone()[0]
    
    conn.close()
    
    text = (
        f'📊 <b>آمار سیستم رفرال</b>\n\n'
        f'📌 <b>آمار کلی:</b>\n'
        f'• کل رفرال‌ها: <b>{total}</b>\n'
        f'• در انتظار خرید: <b>{pending}</b>\n'
        f'• تکمیل شده: <b>{completed}</b>\n'
        f'• دعوت‌کنندگان: <b>{unique_referrers}</b>\n\n'
        f'📈 <b>نرخ تبدیل:</b>\n'
        f'• {int(completed/total*100) if total > 0 else 0}% تکمیل شده'
    )
    
    await callback.message.delete()
    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔙 بازگشت به تنظیمات رفرال",
                callback_data="admin_referral_settings",
                style="danger"
            )]
        ])
    )
    await callback.answer()
# ==================== برگشت به منوی اصلی ====================
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """برگشت به منوی اصلی"""
    await state.clear()
    if "current_order_id" in temp_admin_data:
        del temp_admin_data["current_order_id"]
    
    try:
        await callback.message.delete()
    except:
        pass
    
    class FakeMessage:
        def __init__(self, user_id):
            self.from_user = type('obj', (object,), {'id': user_id})
            self.chat = type('obj', (object,), {'id': user_id})
        
        async def answer(self, text, parse_mode=None, reply_markup=None):
            await callback.message.answer(text, parse_mode=parse_mode, reply_markup=reply_markup)
    
    fake_message = FakeMessage(callback.from_user.id)
    
    from handlers.start import back_to_main_menu
    await back_to_main_menu(fake_message, state)
    await callback.answer()
