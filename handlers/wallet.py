from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from models import User
from database import get_db_connection, get_setting, set_setting
from keyboards.inline_menus import (
    get_wallet_buttons, get_crypto_buttons, get_back_to_main_menu, 
    get_admin_transaction_buttons, get_back_to_wallet,
    get_wallet_advanced_buttons
)
from config import ADMIN_ID, BOT_TOKEN

router = Router()
bot = Bot(token=BOT_TOKEN)

# ================== دیکشنری ایموجی‌های پرمیوم کامل ==================
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
    "loading_purple": "6298412927896520857",
    "skull_rgb": "5771395074600472173",
    "skull_rgb2": "5771859197356413302",
    "gun": "5400238977431122726",
    "money_hand": "5400254220270055279",
    "battery_full": "5972216853324371758",
    "battery_empty1": "5971895340662526314",
    "battery_half": "5972103023806123551",
    "battery_empty2": "5972086930563664925",
    "battery_full2": "5972028501828570123",
    "battery_empty3": "5971846399510186690",
    "dollar_sign": "5400247352617349412",
    "heart_red": "5397699333204226798",
    "heart_black": "5400250874490532265",
    "illuminati": "6220029508456548253",
    "hundred": "6086889112873210296",
    "rules": "4985841557547516692",
    "spray": "4981418681830475148",
    "nitro": "4985622041769018215"
}

class WalletStates(StatesGroup):
    waiting_for_crypto_amount = State()
    waiting_for_crypto_proof = State()
    waiting_for_rial_amount = State()
    waiting_for_rial_proof = State()
    waiting_for_transfer_amount = State()
    waiting_for_transfer_target = State()

temp_deposits = {}
temp_transfers = {}

# ================== کیف پول ==================
@router.message(F.text == "💳 کیف پول")
async def show_wallet(message: Message):
    user_id = message.from_user.id
    
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
    
    balance = User.get_balance(user_id)
    tether_rate = int(get_setting("tether_rate") or 0)
    tron_rate = int(get_setting("tron_rate") or 0)
    
    wallet_text = (
        f'<tg-emoji emoji-id="{PREMIUM["wallet"]}">💳</tg-emoji> '
        f'<b>کیف پول شما</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">📝</tg-emoji> '
        f'<b>موجودی فعلی:</b> <code>{balance:,}</code> تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["chart"]}">🔝</tg-emoji> '
        f'<b>نرخ‌های لحظه‌ای:</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["coin_tether"]}">🪙</tg-emoji> '
        f'تتر (USDT): <b>{tether_rate:,}</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["coin_tron"]}">🪙</tg-emoji> '
        f'ترون (TRX): <b>{tron_rate:,}</b> تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'برای شارژ کیف پول، یکی از گزینه‌های زیر رو انتخاب کن:'
    )
    
    await message.answer(
        wallet_text,
        reply_markup=get_wallet_advanced_buttons(),
        parse_mode="HTML"
    )

# ================== برگشت به کیف پول ==================
@router.callback_query(F.data == "back_to_wallet")
async def back_to_wallet(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if user_id in temp_deposits:
        del temp_deposits[user_id]
    if user_id in temp_transfers:
        del temp_transfers[user_id]
    await state.clear()
    
    balance = User.get_balance(user_id)
    tether_rate = int(get_setting("tether_rate") or 0)
    tron_rate = int(get_setting("tron_rate") or 0)
    
    wallet_text = (
        f'<tg-emoji emoji-id="{PREMIUM["wallet"]}">💳</tg-emoji> '
        f'<b>کیف پول شما</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">📝</tg-emoji> '
        f'<b>موجودی فعلی:</b> <code>{balance:,}</code> تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["chart"]}">🔝</tg-emoji> '
        f'<b>نرخ‌های لحظه‌ای:</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["coin_tether"]}">🪙</tg-emoji> '
        f'تتر (USDT): <b>{tether_rate:,}</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["coin_tron"]}">🪙</tg-emoji> '
        f'ترون (TRX): <b>{tron_rate:,}</b> تومان'
    )
    
    await callback.message.delete()
    await callback.message.answer(
        wallet_text,
        reply_markup=get_wallet_advanced_buttons(),
        parse_mode="HTML"
    )
    await callback.answer()

# ================== نمایش موجودی ==================
@router.callback_query(F.data == "show_balance")
async def show_balance(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    balance = User.get_balance(user_id)
    tether_rate = int(get_setting("tether_rate") or 65000)
    tron_rate = int(get_setting("tron_rate") or 30000)
    
    await callback.message.delete()
    await callback.message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'<b>موجودی کیف پول شما</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">📝</tg-emoji> '
        f'موجودی: <code>{balance:,}</code> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["flying_money"]}">💸</tg-emoji> '
        f'معادل تتر: <code>{balance / tether_rate:.2f}</code> USDT\n'
        f'<tg-emoji emoji-id="{PREMIUM["coin_tron"]}">🪙</tg-emoji> '
        f'معادل ترون: <code>{balance / tron_rate:.2f}</code> TRX\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["star"]}">🟫</tg-emoji> '
        f'برای بازگشت روی دکمه زیر کلیک کن:',
        parse_mode="HTML",
        reply_markup=get_back_to_wallet()
    )

# ================== تاریخچه تراکنش‌ها ==================
@router.callback_query(F.data == "transaction_history")
async def transaction_history(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT amount, status, created_at, currency_type 
        FROM transactions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 10
    ''', (user_id,))
    transactions = cursor.fetchall()
    conn.close()
    
    if not transactions:
        await callback.message.delete()
        await callback.message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["info"]}">ℹ️</tg-emoji> '
            f'<b>هیچ تراکنشی یافت نشد!</b>\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
            f'برای شروع، کیف پول خود را شارژ کنید.',
            parse_mode="HTML",
            reply_markup=get_back_to_wallet()
        )
        return
    
    status_emoji = {
        'pending': f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji>',
        'approved': f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji>',
        'rejected': f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji>'
    }
    
    text = (
        f'<tg-emoji emoji-id="{PREMIUM["history"]}">🔝</tg-emoji> '
        f'<b>تاریخچه تراکنش‌ها</b>\n\n'
    )
    
    for tx in transactions:
        amount, status, created_at, currency_type = tx
        emoji = status_emoji.get(status, '❓')
        type_text = "💳 ریالی" if currency_type == "rial" else "💎 ارزی"
        text += (
            f'{emoji} {type_text} - {amount:,} تومان\n'
            f'<tg-emoji emoji-id="{PREMIUM["time"]}">⏰</tg-emoji> {created_at[:16]}\n'
            f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> {"─" * 15}\n'
        )
    
    await callback.message.delete()
    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_back_to_wallet()
    )

# ================== واریز ارزی ==================
@router.callback_query(F.data == "deposit_crypto")
async def deposit_crypto_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    user_id = callback.from_user.id
    if user_id in temp_deposits:
        del temp_deposits[user_id]
    
    tether_rate = get_setting("tether_rate")
    tron_rate = get_setting("tron_rate")
    
    if tether_rate == "0" or tron_rate == "0" or not tether_rate or not tron_rate:
        await callback.message.delete()
        await callback.message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
            f'<b>نرخ‌های ارز توسط ادمین تنظیم نشده!</b>\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji> '
            f'لطفاً کمی صبر کن یا با پشتیبانی تماس بگیر.\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["earth"]}">🌎</tg-emoji> '
            f'بعد از تنظیم نرخ‌ها، دوباره اقدام کن.',
            parse_mode="HTML",
            reply_markup=get_back_to_wallet()
        )
        await callback.answer()
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'<b>شارژ کیف پول با ارز دیجیتال</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["coin_tether"]}">🪙</tg-emoji> '
        f'نرخ تتر (USDT): <b>{int(tether_rate):,}</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["coin_tron"]}">🪙</tg-emoji> '
        f'نرخ ترون (TRX): <b>{int(tron_rate):,}</b> تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">📝</tg-emoji> '
        f'مبلغ مورد نظر را به <b>تومان</b> وارد کنید:\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["exclamation"]}">‼️</tg-emoji> '
        f'حداقل: <b>۱۰,۰۰۰</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["top"]}">🔝</tg-emoji> '
        f'حداکثر: <b>۱۰۰,۰۰۰,۰۰۰</b> تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'مثال: 100,000  یا  500,000\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["back"]}">📤</tg-emoji> '
        f'برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_wallet()
    )
    await state.set_state(WalletStates.waiting_for_crypto_amount)
    await callback.answer()

@router.message(WalletStates.waiting_for_crypto_amount)
async def get_crypto_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text == "🔙 برگشت به منوی اصلی" or message.text == "🏠 منوی اصلی":
        await state.clear()
        if user_id in temp_deposits:
            del temp_deposits[user_id]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message)
        return
    
    try:
        amount_str = message.text.strip().replace(",", "").replace(" ", "")
        amount = int(amount_str)
        
        if amount <= 0:
            raise ValueError
        if amount < 10000:
            await message.answer(
                f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
                f'<b>حداقل مبلغ شارژ ۱۰,۰۰۰ تومان هست!</b>\n\n'
                f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
                f'لطفاً عدد بزرگتری وارد کن:',
                parse_mode="HTML"
            )
            return
        if amount > 100_000_000:
            await message.answer(
                f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
                f'<b>حداکثر مبلغ شارژ ۱۰۰ میلیون تومان هست!</b>\n\n'
                f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
                f'لطفاً عدد کوچکتری وارد کن:',
                parse_mode="HTML"
            )
            return
    except ValueError:
        await message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
            f'<b>لطفاً یک عدد معتبر وارد کن!</b>\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
            f'مثال: 100,000  یا  500,000',
            parse_mode="HTML"
        )
        return
    
    temp_deposits[user_id] = {
        "amount_toman": amount,
        "type": "crypto"
    }
    
    await message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'<b>مبلغ {amount:,} تومان ثبت شد.</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'حالا انتخاب کن با کدوم ارز میخوای واریز کنی:',
        parse_mode="HTML",
        reply_markup=get_crypto_buttons()
    )
    await state.clear()

# ================== انتخاب تتر ==================
@router.callback_query(F.data == "crypto_tether")
async def select_tether(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if user_id not in temp_deposits or temp_deposits[user_id]["type"] != "crypto":
        await callback.answer(
            f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> خطا! لطفاً از اول شروع کن.',
            show_alert=True
        )
        return
    
    amount_toman = temp_deposits[user_id]["amount_toman"]
    tether_rate = int(get_setting("tether_rate"))
    tether_amount = amount_toman / tether_rate
    
    temp_deposits[user_id]["crypto_type"] = "tether"
    temp_deposits[user_id]["crypto_amount"] = tether_amount
    
    admin_wallet = get_setting("admin_wallet_tether")
    
    await callback.message.delete()
    await callback.message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["coin_tether"]}">🪙</tg-emoji> '
        f'<b>پرداخت با تتر (USDT)</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">📝</tg-emoji> '
        f'مبلغ به تومان: <b>{amount_toman:,}</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["coin_tether"]}">🪙</tg-emoji> '
        f'نرخ تتر: <b>{tether_rate:,}</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'مبلغ قابل پرداخت: <b>{tether_amount:.2f}</b> تتر\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["send"]}">📤</tg-emoji> '
        f'<b>آدرس ولت ادمین (TRC20):</b>\n'
        f'<code>{admin_wallet}</code>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'بعد از واریز، لینک تراکنش یا هش رو برام بفرست\n'
        f'<tg-emoji emoji-id="{PREMIUM["exclamation"]}">‼️</tg-emoji> '
        f'مثال: https://tronscan.org/#/transaction/آدرس_هش\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'لطفاً لینک رو برام بفرست تا بررسی کنم:\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["back"]}">📤</tg-emoji> '
        f'برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_wallet()
    )
    await state.set_state(WalletStates.waiting_for_crypto_proof)
    await callback.answer()

# ================== انتخاب ترون ==================
@router.callback_query(F.data == "crypto_tron")
async def select_tron(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    if user_id not in temp_deposits or temp_deposits[user_id]["type"] != "crypto":
        await callback.answer(
            f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> خطا! لطفاً از اول شروع کن.',
            show_alert=True
        )
        return
    
    amount_toman = temp_deposits[user_id]["amount_toman"]
    tron_rate = int(get_setting("tron_rate"))
    tron_amount = amount_toman / tron_rate
    
    temp_deposits[user_id]["crypto_type"] = "tron"
    temp_deposits[user_id]["crypto_amount"] = tron_amount
    
    admin_wallet = get_setting("admin_wallet_tron")
    
    await callback.message.delete()
    await callback.message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["coin_tron"]}">🪙</tg-emoji> '
        f'<b>پرداخت با ترون (TRX)</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">📝</tg-emoji> '
        f'مبلغ به تومان: <b>{amount_toman:,}</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["coin_tron"]}">🪙</tg-emoji> '
        f'نرخ ترون: <b>{tron_rate:,}</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'مبلغ قابل پرداخت: <b>{tron_amount:.2f}</b> ترون\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["send"]}">📤</tg-emoji> '
        f'<b>آدرس ولت ادمین (TRC20):</b>\n'
        f'<code>{admin_wallet}</code>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'بعد از واریز، لینک تراکنش یا هش رو برام بفرست\n'
        f'<tg-emoji emoji-id="{PREMIUM["exclamation"]}">‼️</tg-emoji> '
        f'مثال: https://tronscan.org/#/transaction/آدرس_هش\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'لطفاً لینک رو برام بفرست تا بررسی کنم:\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["back"]}">📤</tg-emoji> '
        f'برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_wallet()
    )
    await state.set_state(WalletStates.waiting_for_crypto_proof)
    await callback.answer()

# ================== دریافت مدرک ارزی ==================
@router.message(WalletStates.waiting_for_crypto_proof)
async def get_crypto_proof(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text == "🔙 برگشت به منوی اصلی" or message.text == "🏠 منوی اصلی":
        await state.clear()
        if user_id in temp_deposits:
            del temp_deposits[user_id]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message)
        return
    
    proof = message.text.strip()
    
    if user_id not in temp_deposits:
        await message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> '
            f'<b>خطا! لطفاً از اول شروع کن.</b>',
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    if len(proof) < 10:
        await message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
            f'<b>لطفاً یک لینک یا هش معتبر وارد کن!</b>',
            parse_mode="HTML"
        )
        return
    
    temp_deposits[user_id]["proof"] = proof
    
    amount_toman = temp_deposits[user_id]["amount_toman"]
    crypto_type = temp_deposits[user_id]["crypto_type"]
    crypto_amount = temp_deposits[user_id]["crypto_amount"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (user_id, amount, currency_type, crypto_amount, crypto_currency, proof, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    ''', (user_id, amount_toman, 'crypto', crypto_amount, crypto_type, proof))
    conn.commit()
    transaction_id = cursor.lastrowid
    conn.close()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, first_name FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    conn.close()
    
    crypto_name = "تتر (USDT)" if crypto_type == "tether" else "ترون (TRX)"
    admin_text = (
        f'<tg-emoji emoji-id="{PREMIUM["flying_money"]}">💸</tg-emoji> '
        f'<b>درخواست واریز ارزی جدید!</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["user"]}">👤</tg-emoji> کاربر: {user_info["first_name"]}\n'
        f'<tg-emoji emoji-id="{PREMIUM["top"]}">🔝</tg-emoji> آیدی: <code>{user_id}</code>\n'
        f'<tg-emoji emoji-id="{PREMIUM["dragon"]}">🟣</tg-emoji> یوزرنیم: @{user_info["username"] or "ندارد"}\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> {"─" * 15}\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">📝</tg-emoji> مبلغ تومانی: <b>{amount_toman:,}</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> نوع ارز: {crypto_name}\n'
        f'<tg-emoji emoji-id="{PREMIUM["coin_tether"]}">🪙</tg-emoji> مبلغ ارز: <b>{crypto_amount:.2f}</b>\n'
        f'<tg-emoji emoji-id="{PREMIUM["chain"]}">🔗</tg-emoji> لینک تراکنش: {proof}\n'
        f'<tg-emoji emoji-id="{PREMIUM["chart"]}">🔝</tg-emoji> شماره درخواست: <b>{transaction_id}</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> لطفاً بررسی کن و تایید یا رد کن'
    )
    
    await bot.send_message(
        ADMIN_ID,
        admin_text,
        reply_markup=get_admin_transaction_buttons(transaction_id),
        parse_mode="HTML"
    )
    
    await message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'<b>درخواست واریز شما ثبت شد!</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">📝</tg-emoji> '
        f'مبلغ <b>{amount_toman:,}</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'نوع ارز: {crypto_name}\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji> '
        f'به زودی توسط ادمین بررسی و تایید میشه.\n'
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'پس از تایید، موجودی کیف پول شما افزایش پیدا میکنه.\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["star"]}">🟫</tg-emoji> '
        f'از صبر و شکیبایی‌ات متشکرم!',
        parse_mode="HTML",
        reply_markup=get_back_to_main_menu()
    )
    
    del temp_deposits[user_id]
    await state.clear()

# ================== واریز ریالی ==================
@router.callback_query(F.data == "deposit_rial")
async def deposit_rial_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    user_id = callback.from_user.id
    if user_id in temp_deposits:
        del temp_deposits[user_id]
    
    admin_card = get_setting("admin_card_number")
    
    await callback.message.delete()
    await callback.message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["cash"]}">💵</tg-emoji> '
        f'<b>شارژ کیف پول با کارت بانکی</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">📝</tg-emoji> '
        f'مبلغ مورد نظر را به <b>تومان</b> وارد کنید:\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["exclamation"]}">‼️</tg-emoji> '
        f'حداقل: <b>۱۰,۰۰۰</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["top"]}">🔝</tg-emoji> '
        f'حداکثر: <b>۵۰,۰۰۰,۰۰۰</b> تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'مثال: 100,000  یا  500,000\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["back"]}">📤</tg-emoji> '
        f'برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_wallet()
    )
    await state.set_state(WalletStates.waiting_for_rial_amount)
    await callback.answer()

@router.message(WalletStates.waiting_for_rial_amount)
async def get_rial_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if message.text == "🔙 برگشت به منوی اصلی" or message.text == "🏠 منوی اصلی":
        await state.clear()
        if user_id in temp_deposits:
            del temp_deposits[user_id]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message)
        return
    
    try:
        amount_str = message.text.strip().replace(",", "").replace(" ", "")
        amount = int(amount_str)
        
        if amount <= 0:
            raise ValueError
        if amount < 10000:
            await message.answer(
                f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
                f'<b>حداقل مبلغ شارژ ۱۰,۰۰۰ تومان هست!</b>\n\n'
                f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
                f'لطفاً عدد بزرگتری وارد کن:',
                parse_mode="HTML"
            )
            return
        if amount > 50_000_000:
            await message.answer(
                f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
                f'<b>حداکثر مبلغ شارژ ۵۰ میلیون تومان هست!</b>\n\n'
                f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
                f'لطفاً عدد کوچکتری وارد کن:',
                parse_mode="HTML"
            )
            return
    except ValueError:
        await message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
            f'<b>لطفاً یک عدد معتبر وارد کن!</b>\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
            f'مثال: 100,000  یا  500,000',
            parse_mode="HTML"
        )
        return
    
    temp_deposits[user_id] = {
        "amount_toman": amount,
        "type": "rial"
    }
    
    admin_card = get_setting("admin_card_number")
    
    await message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'<b>مبلغ {amount:,} تومان ثبت شد.</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["cash"]}">💵</tg-emoji> '
        f'<b>شماره کارت بانکی برای واریز:</b>\n'
        f'<code>{admin_card}</code>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["user"]}">👤</tg-emoji> '
        f'به نام: مدیریت ربات\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'بعد از واریز، فیش یا رسید بانکی رو برام بفرست\n'
        f'<tg-emoji emoji-id="{PREMIUM["exclamation"]}">‼️</tg-emoji> '
        f'(عکس یا اسکرین‌شات)\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'لطفاً فیش رو برام بفرست تا بررسی کنم:\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["back"]}">📤</tg-emoji> '
        f'برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_wallet()
    )
    await state.set_state(WalletStates.waiting_for_rial_proof)

@router.message(WalletStates.waiting_for_rial_proof, F.photo)
async def get_rial_proof_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    if user_id not in temp_deposits:
        await message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> '
            f'<b>خطا! لطفاً از اول شروع کن.</b>',
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    photo = message.photo[-1]
    file_id = photo.file_id
    
    amount_toman = temp_deposits[user_id]["amount_toman"]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (user_id, amount, currency_type, proof, status)
        VALUES (?, ?, ?, ?, 'pending')
    ''', (user_id, amount_toman, 'rial', file_id))
    conn.commit()
    transaction_id = cursor.lastrowid
    conn.close()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, first_name FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    conn.close()
    
    admin_text = (
        f'<tg-emoji emoji-id="{PREMIUM["cash"]}">💵</tg-emoji> '
        f'<b>درخواست واریز ریالی جدید!</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["user"]}">👤</tg-emoji> کاربر: {user_info["first_name"]}\n'
        f'<tg-emoji emoji-id="{PREMIUM["top"]}">🔝</tg-emoji> آیدی: <code>{user_id}</code>\n'
        f'<tg-emoji emoji-id="{PREMIUM["dragon"]}">🟣</tg-emoji> یوزرنیم: @{user_info["username"] or "ندارد"}\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> {"─" * 15}\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">📝</tg-emoji> مبلغ تومانی: <b>{amount_toman:,}</b> تومان\n'
        f'<tg-emoji emoji-id="{PREMIUM["chart"]}">🔝</tg-emoji> شماره درخواست: <b>{transaction_id}</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> لطفاً فیش رو بررسی کن و تایید یا رد کن'
    )
    
    await bot.send_photo(
        ADMIN_ID,
        photo=file_id,
        caption=admin_text,
        reply_markup=get_admin_transaction_buttons(transaction_id),
        parse_mode="HTML"
    )
    
    await message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'<b>درخواست واریز شما ثبت شد!</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["money"]}">📝</tg-emoji> '
        f'مبلغ <b>{amount_toman:,}</b> تومان\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji> '
        f'به زودی توسط ادمین بررسی و تایید میشه.\n'
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'پس از تایید، موجودی کیف پول شما افزایش پیدا میکنه.\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["star"]}">🟫</tg-emoji> '
        f'از صبر و شکیبایی‌ات متشکرم!',
        parse_mode="HTML",
        reply_markup=get_back_to_main_menu()
    )
    
    del temp_deposits[user_id]
    await state.clear()

@router.message(WalletStates.waiting_for_rial_proof)
async def get_rial_proof_invalid(message: Message):
    await message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
        f'<b>لطفاً عکس فیش واریزی رو ارسال کن!</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'روی 📎 کلیک کن و عکس رو انتخاب کن و بفرست.\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["back"]}">📤</tg-emoji> '
        f'برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_wallet()
    )
