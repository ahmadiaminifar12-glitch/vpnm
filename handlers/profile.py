from aiogram import Router, F
from aiogram.types import Message
from models import User
from database import get_db_connection
from keyboards.inline_menus import get_back_to_main_menu
from datetime import datetime

router = Router()

@router.message(F.text == "👤 حساب کاربری")
async def show_account(message: Message):
    user_id = message.from_user.id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result and result["is_banned"]:
        conn.close()
        await message.answer("⛔ شما مسدود هستید!")
        return
    
    cursor.execute("""
        SELECT user_id, username, first_name, balance, created_at, is_admin 
        FROM users WHERE user_id = ?
    """, (user_id,))
    user = cursor.fetchone()
    
    cursor.execute("""
        SELECT COUNT(*) as total_orders, 
               SUM(total_price) as total_spent,
               SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_orders
        FROM orders WHERE user_id = ?
    """, (user_id,))
    stats = cursor.fetchone()
    
    cursor.execute("""
        SELECT server, volume, duration, total_price, created_at, status
        FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT 1
    """, (user_id,))
    last_order = cursor.fetchone()
    
    conn.close()
    
    created_date = datetime.strptime(user["created_at"], "%Y-%m-%d %H:%M:%S")
    created_fa = created_date.strftime("%Y/%m/%d - %H:%M")
    
    account_text = (
        "<tg-emoji emoji-id=\"4967667085606912536\">👤</tg-emoji> <b>حساب کاربری من</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<tg-emoji emoji-id=\"5032776298733240935\">👁</tg-emoji> <b>نام:</b> {user['first_name']}\n"
        f"<tg-emoji emoji-id=\"4970086827231806362\">➖</tg-emoji> <b>آیدی:</b> <code>{user['user_id']}</code>\n"
        f"<tg-emoji emoji-id=\"5033242607627535090\">🔰</tg-emoji> <b>یوزرنیم:</b> @{user['username'] or 'ندارد'}\n"
        f"<tg-emoji emoji-id=\"4969923081603645985\">📍</tg-emoji> <b>عضو شده از:</b> {created_fa}\n"
        f"<tg-emoji emoji-id=\"4969862428075491925\">🚩</tg-emoji> <b>نوع حساب:</b> {'👑 ادمین' if user['is_admin'] else '⭐ کاربر عادی'}\n\n"
        "<tg-emoji emoji-id=\"4967518033061872209\">💳</tg-emoji> <b>کیف پول:</b>\n"
        f"<tg-emoji emoji-id=\"4967853603151676186\">🔖</tg-emoji> <b>موجودی:</b> {user['balance']:,} تومان\n\n"
        "<tg-emoji emoji-id=\"5033300671290409647\">🛒</tg-emoji> <b>آمار خرید:</b>\n"
        f"<tg-emoji emoji-id=\"5033080906403808074\">📝</tg-emoji> <b>کل سفارشات:</b> {stats['total_orders'] or 0} عدد\n"
        f"<tg-emoji emoji-id=\"4970023558068568720\">🛍️</tg-emoji> <b>سفارشات تکمیل شده:</b> {stats['completed_orders'] or 0} عدد\n"
        f"<tg-emoji emoji-id=\"5032963696746300412\">📃</tg-emoji> <b>مجموع هزینه:</b> {stats['total_spent'] or 0:,} تومان\n\n"
    )
    
    if last_order:
        server_name = "آلمان" if last_order["server"] == "germany" else "آمریکا"
        status_emoji = {
            'pending': '⏳',
            'paid': '✅',
            'completed': '🎉'
        }.get(last_order['status'], '❓')
        
        status_text = {
            'pending': 'در انتظار تایید',
            'paid': 'پرداخت شده',
            'completed': 'تکمیل شده'
        }.get(last_order['status'], 'نامشخص')
        
        account_text += (
            "<tg-emoji emoji-id=\"4970086827231806362\">🆕</tg-emoji> <b>آخرین سفارش:</b>\n"
            f"└ 🌍 {server_name} | 📦 {last_order['volume']} گیگ | ⏰ {last_order['duration']} روز\n"
            f"└ 💰 {last_order['total_price']:,} تومان | وضعیت: {status_emoji} {status_text}\n"
        )
    
    account_text += f"\n<tg-emoji emoji-id=\"4972453139463537420\">⬅️</tg-emoji> <b>برای برگشت به منو از دکمه زیر استفاده کن</b>"
    
    await message.answer(
        account_text,
        reply_markup=get_back_to_main_menu(),
        parse_mode="HTML"
    )
