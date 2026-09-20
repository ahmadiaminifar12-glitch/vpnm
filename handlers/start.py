from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from models import User
from keyboards.main_menu import get_main_menu
from config import ADMIN_ID, BOT_TOKEN
from database import (
    get_setting, 
    is_user_admin, 
    get_or_create_referral_code, 
    get_user_by_referral_code,
    register_referral,
    get_referral_settings
)

router = Router()
bot = Bot(token=BOT_TOKEN)

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    # ===== پردازش کد رفرال =====
    args = message.text.split()
    referrer_id = None
    referral_code = None
    
    if len(args) > 1:
        referral_code = args[1]
        referrer_id = get_user_by_referral_code(referral_code)
    
    user = User.get_or_create(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )
    
    if user["is_banned"]:
        await message.answer("⛔ شما توسط ادمین مسدود شده‌اید!")
        return
    
    # ===== ثبت رفرال =====
    if referrer_id and referrer_id != message.from_user.id:
        settings = get_referral_settings()
        if settings["enabled"] == "on":
            registered = register_referral(referrer_id, message.from_user.id)
            if registered:
                # اطلاع به کاربر دعوت‌کننده
                try:
                    await bot.send_message(
                        referrer_id,
                        f'🎉 <b>یک کاربر جدید با لینک شما وارد شد!</b>\n\n'
                        f'👤 کاربر: {message.from_user.first_name}\n'
                        f'🆔 آیدی: <code>{message.from_user.id}</code>\n\n'
                        f'⭐ پس از اولین خرید، پاداش شما فعال خواهد شد!',
                        parse_mode="HTML"
                    )
                except:
                    pass
    
    # ===== چک جوین اجباری =====
    force_channel = get_setting("force_join_channel")
    if force_channel:
        try:
            member = await bot.get_chat_member(force_channel, message.from_user.id)
            if member.status == "left":
                channel_name = get_setting("force_join_name") or "کانال"
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text=f"🔗 عضویت در {channel_name}",
                        url=f"https://t.me/{force_channel.replace('@', '')}" if force_channel.startswith('@') else f"https://t.me/{force_channel}",
                        style="primary"
                    )],
                    [InlineKeyboardButton(
                        text="🔄 بررسی مجدد",
                        callback_data="check_join",
                        style="success"
                    )]
                ])
                await message.answer(
                    f'🔒 <b>برای استفاده از ربات، ابتدا باید عضو کانال زیر بشی!</b>\n\n'
                    f'🔗 کانال: <b>{channel_name}</b>\n\n'
                    f'🖱 بعد از عضویت، دکمه <b>بررسی مجدد</b> رو بزن.',
                    parse_mode="HTML",
                    reply_markup=keyboard
                )
                return
        except:
            pass
    
    # ===== منوی اصلی =====
    user_first_name = message.from_user.first_name
    user_username = message.from_user.username
    
    if user_username:
        display_name = f"@{user_username}"
    else:
        display_name = user_first_name
    
    start_text = get_setting("start_text") or (
        "✨ 🎉 <b>به ربات فروش کانفیگ آلفا پینگ خوش اومدی!</b> 🎉\n\n"
        f"👋 سلام <code>{display_name}</code>\n\n"
        "💎 <b>اینجا میتونی با بهترین کیفیت و قیمت، وی‌پی‌ان بخری</b>\n\n"
        "⚡ سرعت بالا ⚡\n"
        "📞 پشتیبانی 24/7 📞\n"
        "✅ ضمانت بازگشت وجه (در صورت قطعی سرویس و برطرف نشدن مشکل آن) ✅\n\n"
        "🔽 <b>از منوی زیر یکی رو انتخاب کن</b> 🔽"
    )
    
    is_admin = is_user_admin(message.from_user.id)
    
    await message.answer(
        start_text,
        reply_markup=get_main_menu(is_admin=is_admin),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "check_join")
async def check_join(callback: CallbackQuery, state: FSMContext):
    force_channel = get_setting("force_join_channel")
    if force_channel:
        try:
            member = await bot.get_chat_member(force_channel, callback.from_user.id)
            if member.status != "left":
                await callback.message.delete()
                await cmd_start(callback.message, state)
            else:
                await callback.answer(
                    f'❌ شما هنوز عضو کانال نشدی!',
                    show_alert=True
                )
        except:
            await callback.answer(
                f'❌ خطا در بررسی!',
                show_alert=True
            )
    await callback.answer()


@router.message(F.text.in_(["🔙 بازگشت", "🏠 منوی اصلی"]))
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    is_admin = is_user_admin(message.from_user.id)
    await message.answer(
        "🏠 <b>به منوی اصلی برگشتی!</b>",
        reply_markup=get_main_menu(is_admin=is_admin),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_main")
async def callback_back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    is_admin = is_user_admin(callback.from_user.id)
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer(
        "🏠 <b>به منوی اصلی برگشتی!</b>",
        reply_markup=get_main_menu(is_admin=is_admin),
        parse_mode="HTML"
    )
    await callback.answer()
