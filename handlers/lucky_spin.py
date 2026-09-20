from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from models import User
from database import (
    get_db_connection, 
    get_spin_items, 
    get_spin_item_by_id, 
    get_all_spin_items, 
    get_total_chance, 
    can_user_spin,
    mark_spin_for_order,
    get_last_completed_order_id,
    get_user_spin_count
)
from config import ADMIN_ID, BOT_TOKEN
import random
import asyncio

router = Router()
bot = Bot(token=BOT_TOKEN)

class SpinStates(StatesGroup):
    waiting_for_spin = State()
    waiting_for_admin_reward = State()

temp_spins = {}

# ================== دکمه‌های گردونه (شیشه‌ای آبی) ==================
def get_spin_buttons(items):
    """ایجاد دکمه‌های شیشه‌ای آبی برای آیتم‌های گردونه"""
    buttons = []
    row = []
    
    for idx, item in enumerate(items):
        row.append(InlineKeyboardButton(
            text=f"🎁 {item['name']}",
            callback_data=f"spin_item_{item['id']}",
            style="primary"
        ))
        
        if len(row) == 2:
            buttons.append(row.copy())
            row.clear()
    
    if row:
        buttons.append(row)
    
    buttons.append([
        InlineKeyboardButton(
            text="گردونه شانس",
            callback_data="start_spin",
            style="success"
        )
    ])
    
    buttons.append([
        InlineKeyboardButton(
            text="🔙 بازگشت به منوی اصلی",
            callback_data="back_to_main",
            style="danger"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ================== دکمه‌های گردونه در حالت چرخش (قرمز رندوم) ==================
def get_spinning_buttons(items, selected_id=None):
    """ایجاد دکمه‌های گردونه در حالت چرخش (برخی قرمز)"""
    buttons = []
    row = []
    
    for idx, item in enumerate(items):
        is_red = random.choice([True, False]) if selected_id is None else (item["id"] == selected_id)
        style = "danger" if is_red else "primary"
        
        row.append(InlineKeyboardButton(
            text=f"🎁 {item['name']}",
            callback_data=f"spin_item_{item['id']}",
            style=style
        ))
        
        if len(row) == 2:
            buttons.append(row.copy())
            row.clear()
    
    if row:
        buttons.append(row)
    
    buttons.append([
        InlineKeyboardButton(
            text="⏳ در حال چرخش...",
            callback_data="spinning",
            style="primary"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ================== دکمه‌های گردونه بعد از برنده شدن ==================
def get_winner_buttons(items, winner_id):
    """نمایش دکمه‌ها با برنده سبز و بقیه آبی"""
    buttons = []
    row = []
    
    for idx, item in enumerate(items):
        style = "success" if item["id"] == winner_id else "primary"
        
        row.append(InlineKeyboardButton(
            text=f"🎁 {item['name']}",
            callback_data=f"spin_item_{item['id']}",
            style=style
        ))
        
        if len(row) == 2:
            buttons.append(row.copy())
            row.clear()
    
    if row:
        buttons.append(row)
    
    buttons.append([
        InlineKeyboardButton(
            text="🔄 چرخش دوباره",
            callback_data="spin_again",
            style="success"
        )
    ])
    
    buttons.append([
        InlineKeyboardButton(
            text="🔙 بازگشت به منوی اصلی",
            callback_data="back_to_main",
            style="danger"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# ================== دکمه مخصوص کاربرانی که شرایط ندارن ==================
def get_locked_spin_buttons():
    """دکمه قفل شده برای کاربرانی که خرید جدید ندارن"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔒 قفل شده - نیاز به خرید جدید",
            callback_data="spin_locked",
            style="danger"
        )],
        [InlineKeyboardButton(
            text="🛒 رفتن به بخش خرید",
            callback_data="go_to_buy",
            style="primary"
        )],
        [InlineKeyboardButton(
            text="🔙 بازگشت به منوی اصلی",
            callback_data="back_to_main",
            style="danger"
        )]
    ])

# ================== گردونه شانس (ورودی از منو) ==================
@router.message(F.text == "گردونه شانس 🎰")
async def lucky_spin_start(message: Message, state: FSMContext):
    """نمایش گردونه شانس به کاربر"""
    user_id = message.from_user.id
    
    await state.clear()
    
    # بررسی بن بودن کاربر
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result["is_banned"]:
        await message.answer(
            f'⛔ <b>شما مسدود هستید!</b>',
            parse_mode='HTML'
        )
        return
    
    # ========== شرط اصلی: بررسی خرید جدید ==========
    if not can_user_spin(user_id):
        await message.answer(
            f'🔒 <b>گردونه شانس قفل است!</b>\n\n'
            f'❗ برای باز کردن گردونه شانس، باید یک خرید جدید انجام بدی.\n\n'
            f'🛒 همین حالا برو یه کانفیگ باکیفیت بخر و شانس خودت رو امتحان کن!\n\n'
            f'🎁 جوایز ویژه منتظرت هستن!',
            parse_mode='HTML',
            reply_markup=get_locked_spin_buttons()
        )
        return
    
    # دریافت آیتم‌های گردونه
    items = get_spin_items()
    
    if not items:
        await message.answer(
            f'❗ <b>گردونه شانس در حال حاضر خالی است!</b>\n\n'
            f'🖱 به زودی جوایز جدید اضافه میشه.\n'
            f'⭐ با ما همراه باش!',
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🔙 بازگشت به منوی اصلی",
                    callback_data="back_to_main",
                    style="danger"
                )]
            ])
        )
        return
    
    # ذخیره آیتم‌ها در temp
    temp_spins[user_id] = {
        "items": [dict(item) for item in items],
        "is_spinning": False
    }
    
    # دریافت تعداد کل چرخش‌های کاربر
    total_spins = get_user_spin_count(user_id)
    
    # متن نمایشی
    text = (
        f'🎰 <b>گردونه شانس آلفا پینگ</b>\n\n'
        f'🎉 <b>تبریک! شما یک خرید جدید انجام دادید و گردونه براتون باز شد!</b>\n\n'
        f'📊 تعداد کل چرخش‌های شما: <b>{total_spins}</b>\n\n'
        f'🤎 <b>جوایز امروز:</b>\n'
    )
    
    for item in items:
        text += (
            f'💎 {item["name"]} - <b>{item["chance"]}%</b>\n'
        )
    
    text += (
        f'\n🖱 روی <b>شروع گردونه شانس</b> کلیک کن تا بچرخه!\n'
        f'❗ هر خرید فقط <b>یک بار</b> شانس چرخش داره!\n\n'
        f'❤️ موفق باشی!'
    )
    
    await message.answer(
        text,
        reply_markup=get_spin_buttons(items),
        parse_mode="HTML"
    )

# ================== شروع چرخش گردونه ==================
@router.callback_query(F.data == "start_spin")
async def start_spin(callback: CallbackQuery, state: FSMContext):
    """شروع فرآیند چرخش گردونه"""
    user_id = callback.from_user.id
    
    # ========== بررسی مجدد شرط خرید جدید ==========
    if not can_user_spin(user_id):
        await callback.answer(
            f'🔒 شما خرید جدیدی ندارید!',
            show_alert=True
        )
        return
    
    # بررسی اینکه کاربر در حال چرخش نباشه
    if user_id in temp_spins and temp_spins[user_id].get("is_spinning", False):
        await callback.answer(
            f'🥶 صبر کن گردونه در حال چرخشه!',
            show_alert=True
        )
        return
    
    # دریافت آیتم‌ها
    items = get_spin_items()
    if not items:
        await callback.answer(
            f'❗ گردونه خالی است!',
            show_alert=True
        )
        return
    
    # علامت‌گذاری شروع چرخش
    if user_id not in temp_spins:
        temp_spins[user_id] = {}
    temp_spins[user_id]["is_spinning"] = True
    
    # انتخاب برنده با وزن
    weighted_items = []
    for item in items:
        weighted_items.extend([item["id"]] * item["chance"])
    
    if not weighted_items:
        temp_spins[user_id]["is_spinning"] = False
        await callback.answer(
            f'❗ خطا! لطفاً دوباره تلاش کن.',
            show_alert=True
        )
        return
    
    winner_id = random.choice(weighted_items)
    winner = get_spin_item_by_id(winner_id)
    
    if not winner:
        temp_spins[user_id]["is_spinning"] = False
        await callback.answer(
            f'❗ خطا! لطفاً دوباره تلاش کن.',
            show_alert=True
        )
        return
    
    # ذخیره برنده در temp
    temp_spins[user_id]["winner"] = dict(winner)
    
    # ========== دریافت آخرین سفارش تکمیل شده و ثبت چرخش ==========
    last_order_id = get_last_completed_order_id(user_id)
    if last_order_id:
        mark_spin_for_order(user_id, last_order_id)
    
    # ========== مرحله ۱: چرخش ۵-۶ ثانیه با دکمه‌های قرمز رندوم ==========
    spin_duration = random.randint(5, 6)  # ۵ تا ۶ ثانیه
    steps = spin_duration * 3  # هر ثانیه ۳ بار تغییر
    
    # ارسال پیام اولیه برای چرخش
    await callback.message.delete()
    spin_msg = await callback.message.answer(
        f'🎰 <b>گردونه در حال چرخش...</b>\n\n'
        f'🥶 لطفاً صبر کن!',
        reply_markup=get_spinning_buttons(items),
        parse_mode="HTML"
    )
    
    # حلقه چرخش
    for i in range(steps):
        await asyncio.sleep(0.3)  # هر ۰.۳ ثانیه تغییر
        try:
            await spin_msg.edit_reply_markup(
                reply_markup=get_spinning_buttons(items)
            )
        except:
            pass
    
    # ========== مرحله ۲: نمایش برنده (سبز) ==========
    await asyncio.sleep(0.5)
    
    try:
        await spin_msg.edit_reply_markup(
            reply_markup=get_winner_buttons(items, winner["id"])
        )
    except:
        pass
    
    # ========== مرحله ۳: پیام تبریک به کاربر ==========
    winner_text = (
        f'🏆 <b>تبریک میگم!</b>\n\n'
        f'🎁 شما برنده شدید:\n'
        f'💎 <b>{winner["name"]}</b>\n\n'
        f'ℹ️ {winner["description"]}\n\n'
        f'🖱 به زودی ادمین جایزه رو برات ارسال میکنه.\n'
        f'❤️ موفق باشی!'
    )
    
    await spin_msg.edit_text(
        winner_text,
        reply_markup=get_winner_buttons(items, winner["id"]),
        parse_mode="HTML"
    )
    
    # ========== مرحله ۴: ارسال به ادمین ==========
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, first_name FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    conn.close()
    
    admin_text = (
        f'🏆 <b>برنده گردونه شانس!</b>\n\n'
        f'👤 کاربر: {user_info["first_name"]}\n'
        f'🔝 آیدی: <code>{user_id}</code>\n'
        f'🟣 یوزرنیم: @{user_info["username"] or "ندارد"}\n'
        f'💎 {"─" * 15}\n'
        f'🎁 جایزه برنده: <b>{winner["name"]}</b>\n'
        f'ℹ️ توضیحات: {winner["description"]}\n\n'
        f'🖱 برای ارسال جایزه به کاربر، از دکمه زیر استفاده کن:'
    )
    
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎁 ارسال جایزه به کاربر",
            callback_data=f"send_reward_{user_id}_{winner['id']}",
            style="success"
        )],
        [InlineKeyboardButton(
            text="📊 مشاهده گردونه",
            callback_data="admin_spin_panel",
            style="primary"
        )]
    ])
    
    await bot.send_message(
        ADMIN_ID,
        admin_text,
        reply_markup=admin_keyboard,
        parse_mode="HTML"
    )
    
    # پایان چرخش
    temp_spins[user_id]["is_spinning"] = False
    await callback.answer()

# ================== چرخش دوباره ==================
@router.callback_query(F.data == "spin_again")
async def spin_again(callback: CallbackQuery, state: FSMContext):
    """اجازه چرخش دوباره به کاربر"""
    user_id = callback.from_user.id
    
    # بررسی اینکه خرید جدیدی داره یا نه
    if not can_user_spin(user_id):
        await callback.answer(
            f'🔒 شما خرید جدیدی ندارید!',
            show_alert=True
        )
        return
    
    # پاک کردن temp قبلی
    if user_id in temp_spins:
        temp_spins[user_id] = {}
    
    # دریافت مجدد آیتم‌ها
    items = get_spin_items()
    if not items:
        await callback.answer(
            f'❗ گردونه خالی است!',
            show_alert=True
        )
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'🎰 <b>چرخش دوباره!</b>\n\n'
        f'🎉 <b>تبریک! شما یک خرید جدید انجام دادید!</b>\n\n'
        f'🖱 روی <b>شروع گردونه شانس</b> کلیک کن تا بچرخه!',
        reply_markup=get_spin_buttons(items),
        parse_mode="HTML"
    )
    await callback.answer()

# ================== دکمه قفل شده ==================
@router.callback_query(F.data == "spin_locked")
async def spin_locked(callback: CallbackQuery):
    """وقتی کاربر روی دکمه قفل شده کلیک کنه"""
    await callback.answer(
        f'🔒 برای استفاده از گردونه شانس، یک خرید جدید انجام بده!',
        show_alert=True
    )

# ================== رفتن به بخش خرید ==================
@router.callback_query(F.data == "go_to_buy")
async def go_to_buy_from_spin(callback: CallbackQuery, state: FSMContext):
    """کاربر رو به بخش خرید هدایت کن"""
    await callback.message.delete()
    from handlers.buy import buy_start
    await buy_start(callback.message, state)
    await callback.answer()

# ================== دریافت مشخصات جایزه از ادمین ==================
@router.callback_query(F.data.startswith("send_reward_"))
async def send_reward_to_user(callback: CallbackQuery, state: FSMContext):
    """ادمین میخواهد جایزه را به کاربر ارسال کند"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer(
            f'💀 شما دسترسی ندارید!',
            show_alert=True
        )
        return
    
    parts = callback.data.split("_")
    user_id = int(parts[2])
    item_id = int(parts[3])
    
    item = get_spin_item_by_id(item_id)
    if not item:
        await callback.answer(
            f'❗ جایزه یافت نشد!',
            show_alert=True
        )
        return
    
    temp_spins[f"admin_{callback.from_user.id}"] = {
        "target_user_id": user_id,
        "item_name": item["name"],
        "item_description": item["description"]
    }
    
    await callback.message.delete()
    await callback.message.answer(
        f'🎁 <b>ارسال جایزه به کاربر</b>\n\n'
        f'👤 آیدی کاربر: <code>{user_id}</code>\n'
        f'🎁 جایزه: <b>{item["name"]}</b>\n'
        f'ℹ️ توضیحات: {item["description"]}\n\n'
        f'🖱 لطفاً مشخصات جایزه (متن، کد، فایل یا هر چیزی) رو برام بفرست تا به کاربر ارسال کنم.\n\n'
        f'❗ میتونی متن، عکس، فایل یا هر چیز دیگه‌ای بفرستی.\n\n'
        f'📤 برای لغو، /cancel رو بزن.',
        parse_mode="HTML"
    )
    await state.set_state(SpinStates.waiting_for_admin_reward)
    await callback.answer()

# ================== دریافت متن جایزه از ادمین و ارسال به کاربر ==================
@router.message(SpinStates.waiting_for_admin_reward)
async def process_admin_reward(message: Message, state: FSMContext):
    """ادمین مشخصات جایزه رو فرستاد، ارسال به کاربر"""
    if message.from_user.id != ADMIN_ID:
        return
    
    admin_key = f"admin_{message.from_user.id}"
    if admin_key not in temp_spins:
        await message.answer(
            f'❗ <b>خطا! لطفاً دوباره از دکمه ارسال جایزه استفاده کن.</b>',
            parse_mode="HTML"
        )
        await state.clear()
        return
    
    target_user_id = temp_spins[admin_key]["target_user_id"]
    item_name = temp_spins[admin_key]["item_name"]
    
    try:
        if message.text:
            reward_text = message.text.strip()
            await bot.send_message(
                target_user_id,
                f'🏆 <b>تبریک! شما برنده شدید!</b>\n\n'
                f'🎁 جایزه شما:\n'
                f'💎 <b>{item_name}</b>\n\n'
                f'ℹ️ مشخصات جایزه:\n'
                f'<code>{reward_text}</code>\n\n'
                f'❤️ از همراهی شما متشکریم! 🌟',
                parse_mode="HTML"
            )
        elif message.photo:
            await bot.send_photo(
                target_user_id,
                message.photo[-1].file_id,
                caption=f'🏆 <b>تبریک! شما برنده شدید!</b>\n\n'
                        f'🎁 جایزه شما:\n'
                        f'💎 <b>{item_name}</b>\n\n'
                        f'❤️ از همراهی شما متشکریم! 🌟',
                parse_mode="HTML"
            )
        elif message.document:
            await bot.send_document(
                target_user_id,
                message.document.file_id,
                caption=f'🏆 <b>تبریک! شما برنده شدید!</b>\n\n'
                        f'🎁 جایزه شما:\n'
                        f'💎 <b>{item_name}</b>\n\n'
                        f'❤️ از همراهی شما متشکریم! 🌟',
                parse_mode="HTML"
            )
        else:
            await message.answer(
                f'❗ <b>فرمت پشتیبانی نمیشه!</b>\n\n'
                f'🖱 لطفاً متن، عکس یا فایل ارسال کن.',
                parse_mode="HTML"
            )
            return
        
        await message.answer(
            f'✅ <b>جایزه با موفقیت به کاربر ارسال شد!</b>\n\n'
            f'👤 آیدی: <code>{target_user_id}</code>\n'
            f'🎁 جایزه: {item_name}',
            parse_mode="HTML"
        )
        
        del temp_spins[admin_key]
        await state.clear()
        
    except Exception as e:
        await message.answer(
            f'💀 <b>خطا در ارسال جایزه!</b>\n\n'
            f'ℹ️ ممکن است کاربر ربات رو بلاک کرده باشد.\n'
            f'خطا: {str(e)}',
            parse_mode="HTML"
        )


# ================== برگشت به منوی اصلی ==================
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """برگشت به منوی اصلی"""
    user_id = callback.from_user.id
    
    await state.clear()
    if user_id in temp_spins:
        del temp_spins[user_id]
    
    await callback.message.delete()
    from handlers.start import back_to_main_menu
    await back_to_main_menu(callback.message)
    await callback.answer()
