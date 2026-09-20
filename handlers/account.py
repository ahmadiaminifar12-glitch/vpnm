from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from models import User
from database import get_db_connection
from keyboards.inline_menus import get_back_to_main_menu
from datetime import datetime

router = Router()

# ================== دیکشنری ایموجی‌های پرمیوم ==================
PREMIUM = {
    "user": "4967667085606912536",
    "eye": "5032776298733240935",
    "line": "4970086827231806362",
    "shield": "5033242607627535090",
    "location": "4969923081603645985",
    "flag": "4969862428075491925",
    "wallet": "4967518033061872209",
    "tag": "4967853603151676186",
    "shopping": "5033300671290409647",
    "money": "5033080906403808074",
    "orders": "4970023558068568720",
    "receipt": "5032963696746300412",
    "new": "4970086827231806362",
    "back": "4972453139463537420",
    "diamond": "6084795634143990713",
    "success": "6298804341151107148",
    "danger": "5771395074600472173",
    "loading": "6084846396362462760",
    "star": "5978776771623914876",
    "support": "5971889748615105853",
    "dragon": "6084723220995381369",
    "heart": "5397699333204226798",
    "chart": "6084890063294959714",
    "top": "6084890063294959714",
    "time": "5971895340662526314",
    "energy": "6084367318530397918",
    "money_hand": "5400254220270055279",
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
    "rules": "4985841557547516692",
    "spray": "4981418681830475148",
    "nitro": "4985622041769018215"
}

# ================== حساب کاربری ==================
@router.message(F.text == "👤 حساب کاربری")
async def show_account(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    await state.clear()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result and result["is_banned"]:
        conn.close()
        await message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> '
            f'<b>شما مسدود هستید!</b>',
            parse_mode='HTML'
        )
        return
    
    # اطلاعات کاربر
    cursor.execute("""
        SELECT user_id, username, first_name, balance, created_at, is_admin, is_banned
        FROM users WHERE user_id = ?
    """, (user_id,))
    user = cursor.fetchone()
    
    # آمار سفارشات
    cursor.execute("""
        SELECT 
            COUNT(*) as total_orders,
            SUM(total_price) as total_spent,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_orders,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
            SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) as paid_orders,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_orders
        FROM orders WHERE user_id = ?
    """, (user_id,))
    stats = cursor.fetchone()
    
    # آخرین سفارش
    cursor.execute("""
        SELECT server, volume, duration, total_price, created_at, status
        FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 1
    """, (user_id,))
    last_order = cursor.fetchone()
    
    conn.close()
    
    created_date = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S")
    created_fa = created_date.strftime("%Y/%m/%d - %H:%M")
    
    # وضعیت حساب (با دسترسی مستقیم)
    is_banned = user["is_banned"] if user["is_banned"] is not None else 0
    is_admin = user["is_admin"] if user["is_admin"] is not None else 0
    
    status_emoji = f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji>'
    status_text = "فعال"
    if is_banned:
        status_emoji = f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji>'
        status_text = "مسدود"
    
    # متن اصلی
    account_text = (
        f'<tg-emoji emoji-id="{PREMIUM["user"]}">👤</tg-emoji> '
        f'<b>حساب کاربری من</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'{"─" * 15}\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["eye"]}">👁</tg-emoji> '
        f'<b>نام:</b> {user["first_name"]}\n'
        f'<tg-emoji emoji-id="{PREMIUM["line"]}">➖</tg-emoji> '
        f'<b>آیدی:</b> <code>{user["user_id"]}</code>\n'
        f'<tg-emoji emoji-id="{PREMIUM["shield"]}">🔰</tg-emoji> '
        f'<b>یوزرنیم:</b> @{user["username"] or "ندارد"}\n'
        f'<tg-emoji emoji-id="{PREMIUM["location"]}">📍</tg-emoji> '
        f'<b>عضو شده از:</b> {created_fa}\n'
        f'<tg-emoji emoji-id="{PREMIUM["flag"]}">🚩</tg-emoji> '
        f'<b>نوع حساب:</b> {"👑 ادمین" if is_admin else "⭐ کاربر عادی"}\n'
        f'<tg-emoji emoji-id="{PREMIUM["heart"]}">❤️</tg-emoji> '
        f'<b>وضعیت:</b> {status_emoji} {status_text}\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["wallet"]}">💳</tg-emoji> '
        f'<b>کیف پول:</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["tag"]}">🔖</tg-emoji> '
        f'<b>موجودی:</b> <code>{user["balance"]:,.0f}</code> تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["shopping"]}">🛒</tg-emoji> '
        f'<b>آمار خرید:</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["orders"]}">🛍️</tg-emoji> '
        f'<b>کل سفارشات:</b> {stats["total_orders"] or 0}\n'
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'<b>تکمیل شده:</b> {stats["completed_orders"] or 0}\n'
        f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji> '
        f'<b>در انتظار:</b> {stats["pending_orders"] or 0}\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'<b>پرداخت شده:</b> {stats["paid_orders"] or 0}\n'
        f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> '
        f'<b>رد شده:</b> {stats["rejected_orders"] or 0}\n'
        f'<tg-emoji emoji-id="{PREMIUM["receipt"]}">📃</tg-emoji> '
        f'<b>مجموع هزینه:</b> <code>{stats["total_spent"] or 0:,.0f}</code> تومان\n\n'
    )
    
    # آخرین سفارش
    if last_order:
        server_name = "🇩🇪 آلمان" if last_order["server"] == "germany" else "🇺🇸 آمریکا"
        status_emoji = {
            'pending': f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji>',
            'paid': f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji>',
            'completed': f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji>',
            'rejected': f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji>'
        }.get(last_order['status'], '❓')
        
        status_text = {
            'pending': 'در انتظار تایید',
            'paid': 'پرداخت شده',
            'completed': 'تکمیل شده',
            'rejected': 'رد شده'
        }.get(last_order['status'], 'نامشخص')
        
        account_text += (
            f'<tg-emoji emoji-id="{PREMIUM["new"]}">🆕</tg-emoji> '
            f'<b>آخرین سفارش:</b>\n'
            f'└ {server_name} | 📦 {last_order["volume"]} گیگ | ⏰ {last_order["duration"]} روز\n'
            f'└ 💰 {last_order["total_price"]:,.0f} تومان | وضعیت: {status_emoji} {status_text}\n\n'
        )
    
    account_text += (
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'برای مشاهده جزئیات بیشتر، از دکمه‌های زیر استفاده کن:'
    )
    
    # دکمه‌های پیشرفته
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="موجودی کیف پول", 
            callback_data="show_balance_detail",
            style="success",
            icon_custom_emoji_id=PREMIUM["wallet"]
        )],
        [InlineKeyboardButton(
            text="تاریخچه تراکنش‌ها", 
            callback_data="show_transactions_detail",
            style="primary",
            icon_custom_emoji_id=PREMIUM["chart"]
        )],
        [InlineKeyboardButton(
            text="آمار کامل خرید", 
            callback_data="show_full_stats",
            style="primary",
            icon_custom_emoji_id=PREMIUM["shopping"]
        )],
        [InlineKeyboardButton(
            text="برگشت به منو", 
            callback_data="back_to_main",
            style="danger",
            icon_custom_emoji_id=PREMIUM["back"]
        )]
    ])
    
    await message.answer(
        account_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

# ================== نمایش موجودی دقیق ==================
@router.callback_query(F.data == "show_balance_detail")
async def show_balance_detail(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    
    balance = User.get_balance(user_id)
    
    text = (
        f'<tg-emoji emoji-id="{PREMIUM["wallet"]}">💳</tg-emoji> '
        f'<b>موجودی کیف پول</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">📝</tg-emoji> '
        f'موجودی فعلی: <b>{balance:,.0f}</b> تومان'
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="بازگشت به حساب کاربری", 
                callback_data="back_to_account",
                style="danger",
                icon_custom_emoji_id=PREMIUM["back"]
            )]
        ])
    )

# ================== تاریخچه تراکنش‌ها ==================
@router.callback_query(F.data == "show_transactions_detail")
async def show_transactions_detail(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT amount, status, created_at, currency_type 
        FROM transactions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 10
    """, (user_id,))
    transactions = cursor.fetchall()
    conn.close()
    
    if not transactions:
        await callback.message.edit_text(
            f'<tg-emoji emoji-id="{PREMIUM["info"]}">ℹ️</tg-emoji> '
            f'<b>هیچ تراکنشی یافت نشد!</b>',
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="بازگشت به حساب کاربری", 
                    callback_data="back_to_account",
                    style="danger",
                    icon_custom_emoji_id=PREMIUM["back"]
                )]
            ])
        )
        return
    
    status_emoji = {
        'pending': f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji>',
        'approved': f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji>',
        'rejected': f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji>'
    }
    
    text = (
        f'<tg-emoji emoji-id="{PREMIUM["chart"]}">🔝</tg-emoji> '
        f'<b>۱۰ تراکنش آخر</b>\n\n'
    )
    
    for tx in transactions:
        amount, status, created_at, currency_type = tx
        emoji = status_emoji.get(status, '❓')
        type_text = "💳 ریالی" if currency_type == "rial" else "💎 ارزی"
        text += (
            f'{emoji} {type_text} - {amount:,.0f} تومان\n'
            f'<tg-emoji emoji-id="{PREMIUM["time"]}">⏰</tg-emoji> {created_at[:16]}\n'
            f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> {"─" * 15}\n'
        )
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="بازگشت به حساب کاربری", 
                callback_data="back_to_account",
                style="danger",
                icon_custom_emoji_id=PREMIUM["back"]
            )]
        ])
    )

# ================== آمار کامل خرید ==================
@router.callback_query(F.data == "show_full_stats")
async def show_full_stats(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_orders,
            SUM(total_price) as total_spent,
            AVG(total_price) as avg_price,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_orders,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
            SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) as paid_orders,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_orders
        FROM orders WHERE user_id = ?
    """, (user_id,))
    stats = cursor.fetchone()
    
    cursor.execute("""
        SELECT server, COUNT(*) as count, SUM(total_price) as total
        FROM orders WHERE user_id = ? 
        GROUP BY server
    """, (user_id,))
    servers = cursor.fetchall()
    
    conn.close()
    
    text = (
        f'<tg-emoji emoji-id="{PREMIUM["shopping"]}">🛒</tg-emoji> '
        f'<b>آمار کامل خرید</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["orders"]}">📝</tg-emoji> '
        f'کل سفارشات: <b>{stats["total_orders"] or 0}</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'تکمیل شده: <b>{stats["completed_orders"] or 0}</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji> '
        f'در انتظار: <b>{stats["pending_orders"] or 0}</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'پرداخت شده: <b>{stats["paid_orders"] or 0}</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> '
        f'رد شده: <b>{stats["rejected_orders"] or 0}</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["money_hand"]}">🥇</tg-emoji> '
        f'مجموع هزینه: <b>{stats["total_spent"] or 0:,.0f}</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["chart"]}">🔝</tg-emoji> '
        f'میانگین هزینه: <b>{stats["avg_price"] or 0:,.0f}</b> تومان\n\n'
    )
    
    if servers:
        text += f'<tg-emoji emoji-id="{PREMIUM["earth"]}">🌎</tg-emoji> <b>آمار سرورها:</b>\n'
        for server in servers:
            server_name = "🇩🇪 آلمان" if server["server"] == "germany" else "🇺🇸 آمریکا"
            text += (
                f'• {server_name}: {server["count"]} سفارش - {server["total"]:,.0f} تومان\n'
            )
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="بازگشت به حساب کاربری", 
                callback_data="back_to_account",
                style="danger",
                icon_custom_emoji_id=PREMIUM["back"]
            )]
        ])
    )

# ================== برگشت به حساب کاربری ==================
@router.callback_query(F.data == "back_to_account")
async def back_to_account(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.delete()
    
    class FakeMessage:
        def __init__(self, user_id, text):
            self.from_user = type('obj', (object,), {'id': user_id})
            self.text = text
        
        async def answer(self, *args, **kwargs):
            pass
    
    fake_msg = FakeMessage(callback.from_user.id, "حساب کاربری")
    await show_account(fake_msg, state)
