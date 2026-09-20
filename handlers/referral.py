from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import (
    get_or_create_referral_code,
    get_referral_stats,
    get_referral_settings,
    get_top_referrers,
    get_user
)
from keyboards.main_menu import get_main_menu
from config import BOT_TOKEN

router = Router()
bot = Bot(token=BOT_TOKEN)

# ================== دیکشنری ایموجی‌های پرمیوم ==================
PREMIUM = {
    "link": "6084478403564541578",
    "gift": "4985741377435337443",
    "chart": "6084890063294959714",
    "back": "6087055285157893604",
    "star": "5978776771623914876",
    "user": "6219810752887262728",
    "success": "6298804341151107148",
    "danger": "5771395074600472173",
    "loading": "6084846396362462760",
    "diamond": "6084795634143990713",
}

class ReferralStates(StatesGroup):
    pass

# ================== دکمه رفرال در منو ==================
@router.message(F.text == "🔗 لینک دعوت")
async def show_referral(message: Message):
    """نمایش اطلاعات رفرال کاربر"""
    user_id = message.from_user.id
    
    # دریافت کد رفرال
    code = get_or_create_referral_code(user_id)
    
    # دریافت آمار
    stats = get_referral_stats(user_id)
    settings = get_referral_settings()
    
    # لینک دعوت
    bot_username = (await bot.me()).username
    invite_link = f"https://t.me/{bot_username}?start={code}"
    
    # متن نمایشی
    reward_text = ""
    if settings["enabled"] == "on":
        if settings["reward_type"] == "balance":
            reward_text = f"💰 {settings['reward_amount']:,} تومان"
        elif settings["reward_type"] == "discount":
            reward_text = f"🎯 {settings['discount_percent']}% تخفیف در خرید بعدی"
    else:
        reward_text = "⛔ غیرفعال"
    
    text = (
        f'🔗 <b>سیستم دعوت دوستان</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["link"]}">📎</tg-emoji> '
        f'<b>لینک دعوت شما:</b>\n'
        f'<code>{invite_link}</code>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["gift"]}">🎁</tg-emoji> '
        f'<b>پاداش هر دعوت:</b>\n'
        f'{reward_text}\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["chart"]}">📊</tg-emoji> '
        f'<b>آمار شما:</b>\n'
        f'• کل دعوت‌ها: <b>{stats["total"]}</b>\n'
        f'• در انتظار خرید: <b>{stats["pending"]}</b>\n'
        f'• تکمیل شده: <b>{stats["completed"]}</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["star"]}">⭐</tg-emoji> '
        f'<b>نحوه کار:</b>\n'
        f'1️⃣ لینک خود را برای دوستان بفرست\n'
        f'2️⃣ دوستت با لینک شما وارد ربات شود\n'
        f'3️⃣ پس از اولین خرید یا به صورت آنی، پاداش شما فعال میشود!\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["user"]}">👤</tg-emoji> '
        f'برای مشاهده لیست دوستان دعوت شده، روی دکمه زیر کلیک کن'
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📋 لیست دعوت‌ها",
            callback_data="referral_list",
            style="primary"
        )],
        [InlineKeyboardButton(
            text="📤 اشتراک‌گذاری لینک",
            callback_data="share_referral",
            style="success"
        )],
        [InlineKeyboardButton(
            text="🔙 بازگشت به منو",
            callback_data="back_to_main",
            style="danger"
        )]
    ])
    
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


# ================== لیست دعوت‌ها ==================
@router.callback_query(F.data == "referral_list")
async def referral_list(callback: CallbackQuery):
    """نمایش لیست کاربران دعوت شده"""
    user_id = callback.from_user.id
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r.*, u.first_name, u.username 
        FROM referrals r
        JOIN users u ON r.referred_id = u.user_id
        WHERE r.referrer_id = ?
        ORDER BY r.created_at DESC
        LIMIT 20
    ''', (user_id,))
    referrals = cursor.fetchall()
    conn.close()
    
    if not referrals:
        await callback.message.edit_text(
            f'ℹ️ <b>هنوز هیچ کاربری با لینک شما وارد نشده است!</b>\n\n'
            f'🖱 لینک خود را با دوستانتان به اشتراک بگذارید.',
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🔙 بازگشت به صفحه رفرال",
                    callback_data="referral_back",
                    style="danger"
                )]
            ])
        )
        await callback.answer()
        return
    
    text = f'📋 <b>لیست کاربران دعوت شده</b>\n\n'
    
    for ref in referrals:
        status_emoji = "🟡" if ref["status"] == "pending" else "🟢"
        status_text = "در انتظار خرید" if ref["status"] == "pending" else "✅ تکمیل"
        user_display = ref["first_name"] or ref["username"] or f"کاربر {ref['referred_id']}"
        text += (
            f'{status_emoji} {user_display}\n'
            f'   └ <tg-emoji emoji-id="{PREMIUM["time"]}">⏰</tg-emoji> {ref["created_at"][:16]} | {status_text}\n'
        )
    
    text += f'\nℹ️ <b>تعداد:</b> {len(referrals)} نفر'
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔙 بازگشت به صفحه رفرال",
                callback_data="referral_back",
                style="danger"
            )]
        ])
    )
    await callback.answer()


# ================== اشتراک‌گذاری لینک ==================
@router.callback_query(F.data == "share_referral")
async def share_referral(callback: CallbackQuery):
    """اشتراک‌گذاری لینک دعوت"""
    user_id = callback.from_user.id
    code = get_or_create_referral_code(user_id)
    bot_username = (await bot.me()).username
    invite_link = f"https://t.me/{bot_username}?start={code}"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📤 اشتراک‌گذاری لینک",
            url=f"https://t.me/share/url?url={invite_link}&text=🎁 به ربات فروش کانفیگ آلفا پینگ بپیوند! با لینک دعوت من ثبت نام کن و از تخفیف ویژه استفاده کن!",
            style="primary"
        )],
        [InlineKeyboardButton(
            text="📋 کپی لینک",
            callback_data="copy_referral_link",
            style="primary"
        )],
        [InlineKeyboardButton(
            text="🔙 بازگشت",
            callback_data="referral_back",
            style="danger"
        )]
    ])
    
    await callback.message.edit_text(
        f'📤 <b>اشتراک‌گذاری لینک دعوت</b>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["link"]}">🔗</tg-emoji> '
        f'لینک شما:\n'
        f'<code>{invite_link}</code>\n\n'
        f'<tg-emoji emoji-id="{PREMIUM["mouse_click"]}">🖱</tg-emoji> '
        f'روی دکمه زیر کلیک کن تا لینک را برای دوستانت بفرستی:',
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()


# ================== کپی لینک ==================
@router.callback_query(F.data == "copy_referral_link")
async def copy_referral_link(callback: CallbackQuery):
    """کپی لینک دعوت"""
    user_id = callback.from_user.id
    code = get_or_create_referral_code(user_id)
    bot_username = (await bot.me()).username
    invite_link = f"https://t.me/{bot_username}?start={code}"
    
    await callback.answer(
        f'✅ لینک کپی شد!\n{invite_link}',
        show_alert=True
    )


# ================== جدول برترین‌ها ==================
@router.callback_query(F.data == "referral_top")
async def referral_top(callback: CallbackQuery):
    """نمایش جدول برترین دعوت‌کنندگان"""
    top_users = get_top_referrers(10)
    
    if not top_users or all(u["completed_count"] == 0 for u in top_users):
        await callback.message.edit_text(
            f'🏆 <b>جدول برترین دعوت‌کنندگان</b>\n\n'
            f'ℹ️ <b>هنوز کسی رکوردی ثبت نکرده است!</b>\n\n'
            f'🖱 اولین نفر باش و دوستانت را دعوت کن!',
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="🔙 بازگشت",
                    callback_data="referral_back",
                    style="danger"
                )]
            ])
        )
        await callback.answer()
        return
    
    text = f'🏆 <b>جدول برترین دعوت‌کنندگان</b>\n\n'
    
    emojis = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for i, user in enumerate(top_users[:10]):
        if user["completed_count"] == 0:
            continue
        medal = emojis[i] if i < len(emojis) else f"{i+1}️⃣"
        name = user["first_name"] or user["username"] or f"کاربر {user['user_id']}"
        text += (
            f'{medal} <b>{name}</b>\n'
            f'   └ {user["completed_count"]} دعوت تکمیل شده\n'
        )
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🔙 بازگشت",
                callback_data="referral_back",
                style="danger"
            )]
        ])
    )
    await callback.answer()


# ================== برگشت به صفحه رفرال ==================
@router.callback_query(F.data == "referral_back")
async def referral_back(callback: CallbackQuery):
    """برگشت به صفحه رفرال"""
    await callback.message.delete()
    await show_referral(callback.message)
    await callback.answer()
