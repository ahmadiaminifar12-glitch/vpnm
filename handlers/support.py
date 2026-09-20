from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import (
    get_db_connection, 
    create_ticket, 
    get_user_tickets, 
    get_ticket_by_id,
    get_setting  # <-- این رو اضافه کن
)
from models import User
from keyboards.inline_menus import (
    get_ticket_buttons, 
    get_ticket_list_buttons, 
    get_ticket_detail_buttons, 
    get_back_to_main_menu
)
from config import ADMIN_ID
from aiogram import Bot
from config import BOT_TOKEN

router = Router()
bot = Bot(token=BOT_TOKEN)

class TicketStates(StatesGroup):
    waiting_for_ticket_message = State()

temp_tickets = {}

# ================== دیکشنری ایموجی‌های پرمیوم کامل ==================
PREMIUM = {
    "support": "5971889748615105853",
    "send": "6087055285157893604",
    "success": "6298804341151107148",
    "danger": "5771395074600472173",
    "back": "6087055285157893604",
    "loading": "6084846396362462760",
    "alert": "4990219185784095465",
    "mouse_click": "5400286088927392515",
    "edit": "6086723567653753735",
    "lock": "5400250874490532265",
    "history": "6084890063294959714",
    "user": "6219810752887262728",
    "top": "6084890063294959714",
    "dragon": "6084723220995381369",
    "diamond": "6084795634143990713",
    "heart": "5397699333204226798",
    "flag": "4969862428075491925",
    "exclamation": "6084463229445085650",
    "info": "6087054662387635231",
    "time": "5971895340662526314"
}

# ================== منوی اصلی تیکت ==================
@router.message(F.text == "💬 پشتیبانی")
async def show_support_menu(message: Message):
    """نمایش منوی پشتیبانی با گزینه‌های تیکت"""
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
    
    text = (
        f'<tg-emoji emoji-id="{PREMIUM["support"]}">🎫</tg-emoji> '
        f'<b>سیستم پشتیبانی تیکت‌دهی</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'از طریق گزینه‌های زیر میتونی با تیم پشتیبانی در ارتباط باشی:\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["send"]}">📝</tg-emoji> '
        f'<b>ارسال تیکت جدید:</b> مشکل یا سوال خودت رو مطرح کن\n'
        f'<tg-emoji emoji-id="{PREMIUM["history"]}">📋</tg-emoji> '
        f'<b>مشاهده تیکت‌ها:</b> وضعیت تیکت‌های قبلی رو ببین\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["heart"]}">❤️</tg-emoji> '
        f'تیم پشتیبانی در اسرع وقت پاسخگو خواهد بود.'
    )
    
    await message.answer(
        text,
        reply_markup=get_ticket_buttons(),
        parse_mode="HTML"
    )

# ================== ارسال تیکت جدید ==================
@router.callback_query(F.data == "ticket_new")
async def ticket_new_start(callback: CallbackQuery, state: FSMContext):
    """شروع ارسال تیکت جدید"""
    await state.clear()
    
    user_id = callback.from_user.id
    if user_id in temp_tickets:
        del temp_tickets[user_id]
    
    await callback.message.delete()
    await callback.message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["send"]}">📝</tg-emoji> '
        f'<b>ارسال تیکت جدید</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'لطفاً پیام خود را وارد کنید:\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["exclamation"]}">‼️</tg-emoji> '
        f'مشکل یا سوال خود را به طور کامل شرح دهید.\n'
        f'<tg-emoji emoji-id="{PREMIUM["diamond"]}">💎</tg-emoji> '
        f'هرچه دقیق‌تر توضیح بدی، بهتر میتونیم کمکت کنیم.\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["back"]}">📤</tg-emoji> '
        f'برای لغو، از دکمه زیر استفاده کن',
        parse_mode="HTML",
        reply_markup=get_back_to_main_menu()
    )
    await state.set_state(TicketStates.waiting_for_ticket_message)
    await callback.answer()

@router.message(TicketStates.waiting_for_ticket_message)
async def process_ticket_message(message: Message, state: FSMContext):
    """پردازش پیام تیکت و ذخیره در دیتابیس"""
    user_id = message.from_user.id
    
    if message.text == "🔙 برگشت به منوی اصلی" or message.text == "🏠 منوی اصلی":
        await state.clear()
        if user_id in temp_tickets:
            del temp_tickets[user_id]
        from handlers.start import back_to_main_menu
        await back_to_main_menu(message)
        return
    
    ticket_message = message.text.strip()
    
    if len(ticket_message) < 5:
        await message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> '
            f'<b>پیام باید حداقل ۵ کاراکتر باشه!</b>\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
            f'لطفاً دقیق‌تر توضیح بده:',
            parse_mode="HTML"
        )
        return
    
    # دریافت اطلاعات کاربر
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, first_name FROM users WHERE user_id = ?", (user_id,))
    user_info = cursor.fetchone()
    conn.close()
    
    # ایجاد تیکت در دیتابیس
    ticket_id = create_ticket(
        user_id=user_id,
        username=user_info["username"] or "ندارد",
        first_name=user_info["first_name"] or "کاربر",
        message=ticket_message
    )
    
    # ارسال تیکت به ادمین
    admin_text = (
        f'<tg-emoji emoji-id="{PREMIUM["support"]}">🎫</tg-emoji> '
        f'<b>تیکت جدید دریافت شد!</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["user"]}">👤</tg-emoji> '
        f'کاربر: {user_info["first_name"] or "نامشخص"}\n'
        f'<tg-emoji emoji-id="{PREMIUM["top"]}">🔝</tg-emoji> '
        f'آیدی: <code>{user_id}</code>\n'
        f'<tg-emoji emoji-id="{PREMIUM["dragon"]}">🟣</tg-emoji> '
        f'یوزرنیم: @{user_info["username"] or "ندارد"}\n'
        f'<tg-emoji emoji-id="{PREMIUM["flag"]}">🚩</tg-emoji> '
        f'شماره تیکت: <b>#{ticket_id}</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["send"]}">📤</tg-emoji> '
        f'<b>پیام کاربر:</b>\n{ticket_message}\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'برای پاسخ، از دکمه زیر استفاده کن:'
    )
    
    await bot.send_message(
        ADMIN_ID,
        admin_text,
        parse_mode="HTML",
        reply_markup=get_ticket_detail_buttons(ticket_id, user_id, is_admin=True)
    )
    
    await message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["success"]}">✅</tg-emoji> '
        f'<b>تیکت شما با موفقیت ارسال شد!</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["support"]}">🎫</tg-emoji> '
        f'شماره تیکت: <b>#{ticket_id}</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji> '
        f'به زودی توسط تیم پشتیبانی بررسی و پاسخ داده میشه.\n'
        f'<tg-emoji emoji-id="{PREMIUM["heart"]}">❤️</tg-emoji> '
        f'از صبوری شما متشکریم!',
        parse_mode="HTML",
        reply_markup=get_back_to_main_menu()
    )
    
    await state.clear()

# ================== مشاهده تیکت‌های کاربر ==================
@router.callback_query(F.data == "ticket_list")
async def ticket_list(callback: CallbackQuery):
    """نمایش لیست تیکت‌های کاربر"""
    user_id = callback.from_user.id
    
    tickets = get_user_tickets(user_id)
    
    if not tickets:
        await callback.message.delete()
        await callback.message.answer(
            f'<tg-emoji emoji-id="{PREMIUM["info"]}">ℹ️</tg-emoji> '
            f'<b>هیچ تیکتی یافت نشد!</b>\n\n'
            f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
            f'برای ارسال تیکت جدید، از دکمه <b>ارسال تیکت جدید</b> استفاده کن.',
            parse_mode="HTML",
            reply_markup=get_ticket_buttons()
        )
        await callback.answer()
        return
    
    await callback.message.delete()
    await callback.message.answer(
        f'<tg-emoji emoji-id="{PREMIUM["history"]}">📋</tg-emoji> '
        f'<b>لیست تیکت‌های شما</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'روی هر تیکت کلیک کن تا جزئیات رو ببینی:',
        parse_mode="HTML",
        reply_markup=get_ticket_list_buttons(tickets)
    )
    await callback.answer()

# ================== جزئیات تیکت برای کاربر ==================
@router.callback_query(F.data.startswith("ticket_detail_"))
async def ticket_detail(callback: CallbackQuery):
    """نمایش جزئیات تیکت برای کاربر"""
    user_id = callback.from_user.id
    
    ticket_id = int(callback.data.split("_")[2])
    ticket = get_ticket_by_id(ticket_id)
    
    if not ticket:
        await callback.answer(
            f'<tg-emoji emoji-id="{PREMIUM["alert"]}">🚨</tg-emoji> تیکت یافت نشد!',
            show_alert=True
        )
        return
    
    if ticket["user_id"] != user_id:
        await callback.answer(
            f'<tg-emoji emoji-id="{PREMIUM["danger"]}">💀</tg-emoji> شما دسترسی به این تیکت ندارید!',
            show_alert=True
        )
        return
    
    status_emoji = "🟢" if ticket["status"] == "open" else "🟡" if ticket["status"] == "answered" else "🔴"
    status_text = "باز" if ticket["status"] == "open" else "پاسخ داده شده" if ticket["status"] == "answered" else "بسته"
    
    text = (
        f'<tg-emoji emoji-id="{PREMIUM["support"]}">🎫</tg-emoji> '
        f'<b>تیکت #{ticket["id"]}</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["flag"]}">🚩</tg-emoji> '
        f'وضعیت: {status_emoji} {status_text}\n'
        f'<tg-emoji emoji-id="{PREMIUM["time"]}">⏰</tg-emoji> '
        f'تاریخ: {ticket["created_at"][:16]}\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["send"]}">📤</tg-emoji> '
        f'<b>پیام شما:</b>\n{ticket["message"]}\n\n'
    )
    
    if ticket["admin_answer"]:
        text += (
            f'<tg-emoji emoji-id="{PREMIUM["edit"]}">✏️</tg-emoji> '
            f'<b>پاسخ ادمین:</b>\n{ticket["admin_answer"]}\n\n'
        )
    else:
        text += (
            f'<tg-emoji emoji-id="{PREMIUM["loading"]}">🥶</tg-emoji> '
            f'<i>هنوز پاسخی داده نشده است.</i>\n\n'
        )
    
    text += f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> برای بازگشت از دکمه زیر استفاده کن.'
    
    await callback.message.delete()
    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_ticket_detail_buttons(None, user_id, is_admin=False)
    )
    await callback.answer()

# ================== برگشت به منوی تیکت ==================
@router.callback_query(F.data == "ticket_menu")
async def ticket_menu(callback: CallbackQuery):
    """برگشت به منوی تیکت"""
    await callback.message.delete()
    await show_support_menu(callback.message)
    await callback.answer()

# ================== قوانین و مقررات ==================
@router.message(F.text == "📜 قوانین و مقررات")
async def show_rules(message: Message):
    """نمایش قوانین و مقررات"""
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
    
    # دریافت متن قوانین از دیتابیس
    rules_text = get_setting("rules_text")
    
    if not rules_text:
        # متن پیش‌فرض
        rules_text = (
            "⚜️ <b>قوانین و مقررات ربات</b>\n\n"
            "👍 <b>اولین قانون:</b> ارسال رسید فیک ممنوع می باشد و موجب مسدود شدن سرویس های قبلی شما میگردد\n"
            "👍 <b>دومین قانون:</b> کانفیگ های آلفا پینگ صرفا برای مصرف شخصی می باشند\n"
            "👍 <b>سومین قانون:</b> هرگونه نوع مصرف بر عهده خود کاربر می باشد\n"
            "👍 <b>چهارمین قانون:</b> بازگشت وجه و یا تغییر سرویس به هیچ وجه میسر نمی باشد\n"
            "👍 <b>پنجمین قانون:</b> هرگونه تخلف = مسدودیت دائمی\n"
            "👍 <b>ششمین قانون:</b> در پنل عمده خرید کمتر از 100 گیگ میسر نمی باشد\n\n"
            "🫥 <b>با رعایت قوانین، همیشه بهترین خدمات رو دریافت کن</b>"
        )
    
    await message.answer(
        rules_text,
        reply_markup=get_back_to_main_menu(),
        parse_mode="HTML"
    )
