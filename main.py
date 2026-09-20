import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN
from database import init_database

# ایمپورت مستقیم از هر هندلر
from handlers.start import router as start_router
from handlers.buy import router as buy_router
from handlers.wallet import router as wallet_router
from handlers.account import router as account_router
from handlers.support import router as support_router
from handlers.admin import router as admin_router
from handlers.lucky_spin import router as lucky_spin_router
from handlers.referral import router as referral_router

# تنظیم لاگینگ
logging.basicConfig(level=logging.INFO)

async def set_commands(bot: Bot):
    """تنظیم دستورات ربات"""
    commands = [
        BotCommand(command="start", description="شروع مجدد ربات"),
        BotCommand(command="menu", description="منوی اصلی"),
        BotCommand(command="id", description="دریافت آیدی عددی خود"),
    ]
    await bot.set_my_commands(commands)

async def main():
    # راه‌اندازی دیتابیس
    init_database()
    
    # ایجاد ربات
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # ثبت هندلرها
    dp.include_router(start_router)
    dp.include_router(buy_router)
    dp.include_router(wallet_router)
    dp.include_router(account_router)
    dp.include_router(support_router)
    dp.include_router(admin_router)
    dp.include_router(lucky_spin_router)
    dp.include_router(referral_router)
    
    # تنظیم دستورات
    await set_commands(bot)
    
    # استارت ربات
    logging.info("ربات با موفقیت استارت خورد! 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
