from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from models import User, Order, Product
from database import get_db_connection, get_referral_discount, use_referral_discount, complete_referral
from keyboards.inline_menus import (
    get_server_buttons, get_duration_buttons, get_user_count_buttons,
    get_final_payment_button, get_back_to_main_menu, get_admin_order_buttons,
    get_back_button
)
from config import ADMIN_ID, PRICES, BOT_TOKEN
import asyncio
import datetime

router = Router()
bot = Bot(token=BOT_TOKEN)

# ================== دیکشنری ایموجی‌های پرمیوم ==================
PREMIUM = {
    "server": "6084478403564541578",
    "money": "5400254220270055279",
    "time": "5971895340662526314",
    "user": "6219810752887262728",
    "success": "6298804341151107148",
    "danger": "5771395074600472173",
    "back": "6087055285157893604",
    "loading": "6084846396362462760",
    "star": "5978776771623914876",
    "diamond": "6084795634143990713",
    "dragon": "6084723220995381369",
    "chart": "6084890063294959714",
    "top": "6084890063294959714",
    "heart": "5397699333204226798",
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
    "wallet": "4967518033061872209",
    "shield": "5033242607627535090",
    "flag": "4969862428075491925"
}

class BuyStates(StatesGroup):
    waiting_for_volume = State()

temp_orders = {}
temp_orders_lock = asyncio.Lock()

USER_COUNT_PRICES = {
    1: 10000,
    2: 20000,
    3: 30000
}

# ================== توابع کمکی ==================
def has_pending_order(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM orders WHERE user_id = ? AND status = 'pending'", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_volume_discount(volume):
    """محاسبه تخفیف بر اساس حجم"""
    if volume >= 100:
        return 0.20
    elif volume >= 50:
        return 0.15
    elif volume >= 30:
        return 0.10
    elif volume >= 15:
        return 0.05
    else:
        return 0

def get_volume_bonus(volume):
    """محاسبه حجم جایزه بر اساس حجم"""
    if volume >= 100:
        return 15
    elif volume >= 50:
        return 8
    elif volume >= 30:
        return 5
    elif volume >= 15:
        return 2
    else:
        return 0

# ================== خرید شروع ==================
@router.message(F.text == "🛒 خرید حجم")
async def buy_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    await state.clear()
    temp_orders.pop(user_id, None)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result["is_banned"]:
        await message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> '
            f'<b>شما مسدود هستید!</b>',
            parse_mode='HTML'
        )
        return
    
    if has_pending_order(user_id):
        await message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
            f'<b>شما یک سفارش در انتظار تایید دارید!</b>\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji> '
            f'تا زمانی که سفارش قبلی شما توسط ادمین تایید یا رد نشده، نمی‌توانید سفارش جدید ثبت کنید.',
            parse_mode='HTML'
        )
        return
    
    products = Product.get_all()
    active_products = [p for p in products if p["is_active"]]
    
    if not active_products:
        await message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
            f'<b>هیچ سروری برای فروش وجود ندارد!</b>',
            parse_mode='HTML'
        )
        return
    
    text = (
        f'<tg-emoji emoji-id="{PREMIUM["server"]}">🔗</tg-emoji> '
        f'<b>انتخاب سرور</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'سرور مورد نظرت رو انتخاب کن:\n\n'
    )
    
    for p in active_products:
        text += (
            f'<tg-emoji emoji-id="{PREMIUM["shield"]}">🔰</tg-emoji> '
            f'<b>{p["name"]}</b> - هر گیگ {p["price_per_gb"]:,} تومان\n'
        )
    
    await message.answer(
        text,
        reply_markup=get_server_buttons(),
        parse_mode="HTML"
    )

# ================== انتخاب سرور ==================
@router.callback_query(F.data.startswith("server_"))
async def select_server(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    await state.clear()
    async with temp_orders_lock:
        if user_id in temp_orders:
            del temp_orders[user_id]
    
    product_id = int(callback.data.split("_")[1])
    product = Product.get_by_id(product_id)
    
    if not product or not product["is_active"]:
        await callback.answer(
            f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> این سرور در حال حاضر موجود نیست!',
            show_alert=True
        )
        return
    
    async with temp_orders_lock:
        temp_orders[user_id] = {
            "product_id": product["id"],
            "server": product["name"],
            "price_per_gb": product["price_per_gb"],
            "button_color": product["button_color"]
        }
    
    await callback.message.delete()
    await callback.message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'<b>سرور {product["name"]} انتخاب شد!</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">🥇</tg-emoji> '
        f'قیمت هر گیگ: <b>{product["price_per_gb"]:,}</b> تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'حجم مورد نظرت رو به گیگ وارد کن:\n'
        f'<tg-emoji emoji-id="{PREMIUM["exclamation"]}">‼️</tg-emoji> '
        f'مثال: 10، 20، 50، 100\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["percent"]}">💯</tg-emoji> '
        f'هرچی حجم بیشتر، تخفیف بیشتر!\n'
        f'<tg-emoji emoji-id="{PREMIUM["gift"]}">🤎</tg-emoji> '
        f'حجم بالای ۱۵ گیگ جایزه حجمی داره!\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["back"]}">📤</tg-emoji> '
        f'برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_button()
    )
    
    await state.set_state(BuyStates.waiting_for_volume)
    await callback.answer()

# ================== برگشت به انتخاب سرور ==================
@router.callback_query(F.data == "back_to_server")
async def back_to_server(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    await state.clear()
    async with temp_orders_lock:
        if user_id in temp_orders:
            del temp_orders[user_id]
    
    products = Product.get_all()
    active_products = [p for p in products if p["is_active"]]
    
    text = (
        f'<tg-emoji emoji-id="{PREMIUM["server"]}">🔗</tg-emoji> '
        f'<b>انتخاب سرور</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'سرور مورد نظرت رو انتخاب کن:\n\n'
    )
    
    for p in active_products:
        text += (
            f'<tg-emoji emoji-id="{PREMIUM["shield"]}">🔰</tg-emoji> '
            f'<b>{p["name"]}</b> - هر گیگ {p["price_per_gb"]:,} تومان\n'
        )
    
    await callback.message.delete()
    await callback.message.answer(text, reply_markup=get_server_buttons(), parse_mode="HTML")
    await callback.answer()

# ================== دریافت حجم ==================
@router.message(BuyStates.waiting_for_volume)
async def get_volume(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text == "🔙 برگشت به منوی اصلی" or message.text == "🏠 منوی اصلی":
        await state.clear()
        async with temp_orders_lock:
            if user_id in temp_orders:
                del temp_orders[user_id]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message, state)
        return
    
    async with temp_orders_lock:
        if user_id not in temp_orders:
            await state.clear()
            await message.answer(
                f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
                f'<b>زمان خرید منقضی شد!</b>\n\n'
                f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
                f'لطفاً دوباره از اول شروع کن.',
                parse_mode="HTML",
                reply_markup=get_back_to_main_menu()
            )
            return
        
        try:
            volume = int(message.text.strip())
            if volume <= 0:
                raise ValueError
            if volume > 1000:
                await message.answer(
                    f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
                    f'<b>حجم حداکثر ۱۰۰۰ گیگ قابل سفارش هست!</b>\n\n'
                    f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
                    f'لطفاً عدد کمتری وارد کن:',
                    parse_mode="HTML"
                )
                return
        except ValueError:
            await message.answer(
                f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
                f'<b>لطفاً یک عدد معتبر وارد کن!</b>\n\n'
                f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
                f'مثال: 10، 20، 50، 100',
                parse_mode="HTML"
            )
            return
        
        base_price = volume * temp_orders[user_id]["price_per_gb"]
        discount = get_volume_discount(volume)
        bonus = get_volume_bonus(volume)
        final_price = base_price * (1 - discount)
        
        temp_orders[user_id]["volume"] = volume
        temp_orders[user_id]["base_price"] = base_price
        temp_orders[user_id]["discount"] = discount
        temp_orders[user_id]["bonus"] = bonus
        temp_orders[user_id]["final_price"] = final_price
    
    discount_text = f" (تخفیف {int(discount*100)}%)" if discount > 0 else ""
    bonus_text = f"\n<tg-emoji emoji-id='{PREMIUM["gift"]}'>🤎</tg-emoji> <b>حجم جایزه:</b> +{bonus} گیگ" if bonus > 0 else ""
    
    await message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'<b>حجم {volume} گیگ ثبت شد!</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["server"]}">🔗</tg-emoji> '
        f'سرور: <b>{temp_orders[user_id]["server"]}</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">🥇</tg-emoji> '
        f'قیمت پایه: {base_price:,} تومان{discount_text}\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'قیمت نهایی حجم: {final_price:,.0f} تومان{bonus_text}\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["time"]}">⏰</tg-emoji> '
        f'حالا مدت زمان سرویس رو انتخاب کن:\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> '
        f'۳۰ روزه → +{PRICES["days_30"]:,} تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'۶۰ روزه → +{PRICES["days_60"]:,} تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'۹۰ روزه → +{PRICES["days_90"]:,} تومان',
        parse_mode="HTML",
        reply_markup=get_duration_buttons()
    )
    
    await state.clear()

# ================== برگشت به انتخاب مدت ==================
@router.callback_query(F.data == "back_to_duration")
async def back_to_duration(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    await state.clear()
    
    async with temp_orders_lock:
        if user_id not in temp_orders:
            await callback.answer(
                f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> خطا! لطفاً از اول شروع کن.',
                show_alert=True
            )
            await callback.message.delete()
            return
        
        volume = temp_orders[user_id]["volume"]
        final_price = temp_orders[user_id]["final_price"]
    
    await callback.message.delete()
    await callback.message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["time"]}">⏰</tg-emoji> '
        f'<b>مدت زمان سرویس</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["server"]}">🔗</tg-emoji> '
        f'سرور: {temp_orders[user_id]["server"]}\n'
        f'<tg-emoji emoji-id="{PREMIUM["chart"]}">🔝</tg-emoji> '
        f'حجم: {volume} گیگ - {final_price:,.0f} تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'مدت زمان مورد نظر رو انتخاب کن:\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> '
        f'۳۰ روزه → +{PRICES["days_30"]:,} تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'۶۰ روزه → +{PRICES["days_60"]:,} تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'۹۰ روزه → +{PRICES["days_90"]:,} تومان',
        parse_mode="HTML",
        reply_markup=get_duration_buttons()
    )
    await callback.answer()

# ================== انتخاب مدت زمان ==================
@router.callback_query(F.data.startswith("duration_"))
async def select_duration(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    await state.clear()
    
    async with temp_orders_lock:
        if user_id not in temp_orders:
            await callback.answer(
                f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> خطا! لطفاً از اول شروع کن.',
                show_alert=True
            )
            await callback.message.delete()
            return
        
        duration = int(callback.data.split("_")[1])
        duration_prices = {30: PRICES["days_30"], 60: PRICES["days_60"], 90: PRICES["days_90"]}
        duration_price = duration_prices[duration]
        
        temp_orders[user_id]["duration"] = duration
        temp_orders[user_id]["duration_price"] = duration_price
    
    duration_names = {30: "۳۰ روزه", 60: "۶۰ روزه", 90: "۹۰ روزه"}
    
    await callback.message.delete()
    await callback.message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'<b>مدت {duration_names[duration]} انتخاب شد!</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">🥇</tg-emoji> '
        f'هزینه تمدید: +{duration_price:,} تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["user"]}">👤</tg-emoji> '
        f'حالا تعداد کاربران سرویس رو انتخاب کن:\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'تک کاربره → +{USER_COUNT_PRICES[1]:,} تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> '
        f'دو کاربره → +{USER_COUNT_PRICES[2]:,} تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'سه کاربره → +{USER_COUNT_PRICES[3]:,} تومان',
        parse_mode="HTML",
        reply_markup=get_user_count_buttons()
    )
    await callback.answer()

# ================== انتخاب تعداد کاربر ==================
@router.callback_query(F.data.startswith("usercount_"))
async def select_user_count(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    await state.clear()
    
    async with temp_orders_lock:
        if user_id not in temp_orders:
            await callback.answer(
                f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> خطا! لطفاً از اول شروع کن.',
                show_alert=True
            )
            await callback.message.delete()
            return
        
        user_count = int(callback.data.split("_")[1])
        user_count_price = USER_COUNT_PRICES[user_count]
        
        user_count_names = {1: "تک کاربره", 2: "دو کاربره", 3: "سه کاربره"}
        
        temp_orders[user_id]["user_count"] = user_count
        temp_orders[user_id]["user_count_name"] = user_count_names[user_count]
        temp_orders[user_id]["user_count_price"] = user_count_price
        
        total_price = temp_orders[user_id]["final_price"] + temp_orders[user_id]["duration_price"] + user_count_price
        temp_orders[user_id]["total_price"] = total_price
    
    # ===== دریافت تخفیف رفرال =====
    referral_discount = get_referral_discount(user_id)
    discount_amount = 0
    discount_percent = 0
    
    if referral_discount > 0:
        discount_percent = referral_discount
        discount_amount = int(total_price * referral_discount / 100)
        total_price_after_discount = total_price - discount_amount
        # استفاده از تخفیف
        use_referral_discount(user_id)
    else:
        total_price_after_discount = total_price
    
    balance = User.get_balance(user_id)
    discount_text = f" (تخفیف {int(temp_orders[user_id]['discount']*100)}%)" if temp_orders[user_id]['discount'] > 0 else ""
    
    # ===== متن تخفیف رفرال =====
    referral_text = ""
    if discount_percent > 0:
        referral_text = (
            f'\n<tg-emoji emoji-id="{PREMIUM["gift"]}">🎁</tg-emoji> '
            f'<b>تخفیف رفرال:</b> {discount_percent}% ({discount_amount:,} تومان)\n'
        )
    
    invoice_text = (
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'<b>فاکتور خرید شما</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["server"]}">🔗</tg-emoji> '
        f'سرور: <b>{temp_orders[user_id]["server"]}</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["chart"]}">🔝</tg-emoji> '
        f'حجم: <b>{temp_orders[user_id]["volume"]}</b> گیگ\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">🥇</tg-emoji> '
        f'قیمت حجم: {temp_orders[user_id]["final_price"]:,.0f} تومان{discount_text}\n'
        f'<tg-emoji emoji-id="{PREMIUM["time"]}">⏰</tg-emoji> '
        f'مدت زمان: <b>{temp_orders[user_id]["duration"]}</b> روز\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">🥇</tg-emoji> '
        f'هزینه تمدید: +{temp_orders[user_id]["duration_price"]:,} تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["user"]}">👤</tg-emoji> '
        f'تعداد کاربر: <b>{temp_orders[user_id]["user_count_name"]}</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">🥇</tg-emoji> '
        f'هزینه کاربران: +{user_count_price:,} تومان'
    )
    
    if discount_percent > 0:
        invoice_text += f'\n{referral_text}'
    
    invoice_text += (
        f'\n<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'{"─" * 15}\n'
        f'<tg-emoji emoji-id="{PREMIUM["winner"]}">🤎</tg-emoji> '
        f'<b>قیمت نهایی:</b> {total_price_after_discount:,.0f} تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["wallet"]}">💳</tg-emoji> '
        f'موجودی کیف پول: <b>{balance:,}</b> تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["exclamation"]}">‼️</tg-emoji> '
        f'بعد از پرداخت، ادمین اطلاعات سرور رو برات ارسال میکنه\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'برای تایید نهایی روی دکمه زیر کلیک کن:'
    )
    
    # ذخیره قیمت نهایی با تخفیف در temp
    temp_orders[user_id]["total_price_after_discount"] = total_price_after_discount
    
    await callback.message.delete()
    await callback.message.answer(
        invoice_text,
        parse_mode="HTML",
        reply_markup=get_final_payment_button()
    )
    await callback.answer()

# ================== پرداخت نهایی ==================
@router.callback_query(F.data == "final_payment")
async def final_payment(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    await state.clear()
    
    async with temp_orders_lock:
        if user_id not in temp_orders:
            await callback.answer(
                f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> خطا! لطفاً از اول شروع کن.',
                show_alert=True
            )
            await callback.message.delete()
            return
        
        if has_pending_order(user_id):
            await callback.message.delete()
            await callback.message.answer(
                f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
                f'<b>شما یک سفارش در انتظار تایید دارید!</b>\n\n'
                f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji> '
                f'تا زمانی که سفارش قبلی شما توسط ادمین تایید یا رد نشده، نمی‌توانید سفارش جدید ثبت کنید.',
                parse_mode="HTML",
                reply_markup=get_back_to_main_menu()
            )
            await callback.answer()
            return
        
        # استفاده از قیمت با تخفیف
        total_price = temp_orders[user_id].get("total_price_after_discount", temp_orders[user_id]["total_price"])
        balance = User.get_balance(user_id)
        
        if balance < total_price:
            diff = total_price - balance
            await callback.message.delete()
            await callback.message.answer(
                f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
                f'<b>موجودی کیف پول شما کافی نیست!</b>\n\n'
                f'<tg-emoji emoji-id="{PREMIUM["money"]}">🥇</tg-emoji> '
                f'قیمت فاکتور: <b>{total_price:,}</b> تومان\n'
                f'<tg-emoji emoji-id="{PREMIUM["wallet"]}">💳</tg-emoji> '
                f'موجودی شما: <b>{balance:,}</b> تومان\n'
                f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> '
                f'مبلغ کمبود: <b>{diff:,}</b> تومان\n\n'
                f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
                f'لطفاً از بخش کیف پول حساب خودت رو شارژ کن و دوباره اقدام کن.',
                parse_mode="HTML",
                reply_markup=get_back_to_main_menu()
            )
            del temp_orders[user_id]
            return
        
        new_balance = balance - total_price
        User.update_balance(user_id, new_balance)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (user_id, server, server_name, volume, duration, user_count, user_count_price, total_price, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (
            user_id,
            temp_orders[user_id]["server"],
            temp_orders[user_id]["server"],
            temp_orders[user_id]["volume"],
            temp_orders[user_id]["duration"],
            temp_orders[user_id]["user_count"],
            temp_orders[user_id]["user_count_price"],
            total_price
        ))
        conn.commit()
        order_id = cursor.lastrowid
        
        # ===== دریافت اطلاعات کاربر (قبل از استفاده در رفرال) =====
        cursor.execute("SELECT username, first_name FROM users WHERE user_id = ?", (user_id,))
        user_info = cursor.fetchone()
        
        # ===== تکمیل رفرال (اگر کاربر با لینک دعوت وارد شده باشد) =====
        try:
            # بررسی اینکه کاربر با لینک رفرال وارد شده یا نه
            cursor.execute("SELECT referred_by FROM users WHERE user_id = ?", (user_id,))
            user_data = cursor.fetchone()
            
            if user_data and user_data["referred_by"] and user_data["referred_by"] != 0:
                # تکمیل رفرال
                result = complete_referral(user_id)
                if result:
                    # دریافت اطلاعات کاربر دعوت‌کننده
                    cursor.execute("SELECT first_name FROM users WHERE user_id = ?", (user_data["referred_by"],))
                    referrer = cursor.fetchone()
                    if referrer:
                        print(f"✅ رفرال کاربر {user_id} توسط {referrer['first_name']} تکمیل شد")
                        
                        # اطلاع به ادمین
                        admin_notify = (
                            f'🎉 <b>رفرال جدید تکمیل شد!</b>\n\n'
                            f'👤 کاربر دعوت‌کننده: {referrer["first_name"]}\n'
                            f'👤 کاربر جدید: {user_info["first_name"]}\n'
                            f'🆔 آیدی کاربر جدید: <code>{user_id}</code>\n'
                            f'💰 مبلغ خرید: {total_price:,} تومان'
                        )
                        await bot.send_message(ADMIN_ID, admin_notify, parse_mode="HTML")
                else:
                    print(f"ℹ️ رفرال برای کاربر {user_id} پیدا نشد یا قبلاً تکمیل شده")
        except Exception as e:
            print(f"⚠️ خطا در تکمیل رفرال: {e}")
        
        conn.close()
        
        user_count_names = {1: "تک کاربره", 2: "دو کاربره", 3: "سه کاربره"}
        
        admin_text = (
            f'<tg-emoji emoji-id="{PREMIUM["fire"]}">🔥</tg-emoji> '
            f'<b>سفارش جدید دریافت شد!</b>\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["user"]}">👤</tg-emoji> '
            f'کاربر: {user_info["first_name"]}\n'
            f'<tg-emoji emoji-id="{PREMIUM["top"]}">🔝</tg-emoji> '
            f'آیدی: <code>{user_id}</code>\n'
            f'<tg-emoji emoji-id="{PREMIUM["dragon"]}">🟣</tg-emoji> '
            f'یوزرنیم: @{user_info["username"] or "ندارد"}\n'
            f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
            f'{"─" * 15}\n'
            f'<tg-emoji emoji-id="{PREMIUM["server"]}">🔗</tg-emoji> '
            f'سرور: {temp_orders[user_id]["server"]}\n'
            f'<tg-emoji emoji-id="{PREMIUM["chart"]}">🔝</tg-emoji> '
            f'حجم: {temp_orders[user_id]["volume"]} گیگ\n'
            f'<tg-emoji emoji-id="{PREMIUM["time"]}">⏰</tg-emoji> '
            f'مدت: {temp_orders[user_id]["duration"]} روز\n'
            f'<tg-emoji emoji-id="{PREMIUM["user"]}">👤</tg-emoji> '
            f'تعداد کاربر: {user_count_names[temp_orders[user_id]["user_count"]]}\n'
            f'<tg-emoji emoji-id="{PREMIUM["money"]}">🥇</tg-emoji> '
            f'مبلغ: {total_price:,} تومان\n'
            f'<tg-emoji emoji-id="{PREMIUM["chart"]}">🔝</tg-emoji> '
            f'شماره سفارش: <b>{order_id}</b>\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
            f'لطفاً پس از بررسی، اطلاعات کانفیگ رو براش بفرست'
        )
        
        await bot.send_message(
            ADMIN_ID,
            admin_text,
            parse_mode="HTML",
            reply_markup=get_admin_order_buttons(order_id)
        )
        
        await callback.message.delete()
        await callback.message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
            f'<b>پرداخت با موفقیت انجام شد!</b>\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["money"]}">🥇</tg-emoji> '
            f'مبلغ <b>{total_price:,}</b> تومان از کیف پول شما کسر شد.\n'
            f'<tg-emoji emoji-id="{PREMIUM["wallet"]}">💳</tg-emoji> '
            f'موجودی جدید: <b>{new_balance:,}</b> تومان\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["chart"]}">🔝</tg-emoji> '
            f'سفارش شما با شماره <b>#{order_id}</b> ثبت شد.\n'
            f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji> '
            f'به زودی ادمین اطلاعات سرور رو برات ارسال میکنه.\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["winner"]}">🤎</tg-emoji> '
            f'از خریدت متشکرم! 🌟',
            parse_mode="HTML",
            reply_markup=get_back_to_main_menu()
        )
        
        del temp_orders[user_id]
    
    await callback.answer()

# ================== برگشت به منوی اصلی ==================
@router.callback_query(F.data == "back_to_main")
async def global_back_to_main(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    await state.clear()
    async with temp_orders_lock:
        if user_id in temp_orders:
            del temp_orders[user_id]
    
    await callback.message.delete()
    from handlers.start import back_to_main_menu
    await back_to_main_menu(callback.message, state)
    await callback.answer()

@router.message(F.text == "🏠 منوی اصلی")
async def global_main_menu(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    await state.clear()
    async with temp_orders_lock:
        if user_id in temp_orders:
            del temp_orders[user_id]
    
    from handlers.start import back_to_main_menu
    await back_to_main_menu(message, state)
