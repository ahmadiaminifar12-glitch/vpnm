import sqlite3
import os
from config import DEFAULT_SETTINGS, ADMIN_ID
from datetime import datetime

DB_PATH = "bot.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """ساخت دیتابیس از اول با تمام جدول‌ها"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ================== جدول users ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            balance INTEGER DEFAULT 0,
            is_banned BOOLEAN DEFAULT 0,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            safe_amount INTEGER DEFAULT 0,
            safe_duration INTEGER DEFAULT 0,
            safe_start TEXT,
            safe_interest INTEGER DEFAULT 0,
            daily_interest INTEGER DEFAULT 0,
            last_daily_check TEXT,
            total_earned INTEGER DEFAULT 0,
            total_deposits INTEGER DEFAULT 0,
            total_withdraws INTEGER DEFAULT 0,
            last_daily_interest_date TEXT,
            bank_card TEXT,
            bank_name TEXT,
            spin_count INTEGER DEFAULT 0,
            last_spin_date TEXT,
            last_spin_order_id INTEGER DEFAULT 0,
            referral_code TEXT UNIQUE,
            referral_count INTEGER DEFAULT 0,
            referral_discount INTEGER DEFAULT 0,
            referred_by INTEGER DEFAULT 0
        )
    ''')
    
    # ================== جدول settings ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT
        )
    ''')
    
    # ================== جدول orders ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            server TEXT,
            server_name TEXT,
            volume INTEGER,
            duration INTEGER,
            user_count INTEGER DEFAULT 1,
            user_count_price INTEGER DEFAULT 0,
            total_price INTEGER,
            status TEXT DEFAULT 'pending',
            config_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # ================== جدول transactions ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER,
            currency_type TEXT,
            crypto_amount REAL,
            crypto_currency TEXT,
            proof TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # ================== جدول admin_logs ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_id INTEGER,
            action TEXT,
            target_user_id INTEGER,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (admin_id) REFERENCES users (user_id)
        )
    ''')
    
    # ================== جدول products ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price_per_gb INTEGER NOT NULL,
            button_color TEXT DEFAULT 'primary',
            flag TEXT DEFAULT '',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ================== جدول crypto_requests ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS crypto_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            currency TEXT NOT NULL,
            address TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # ================== جدول charge_requests ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS charge_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            method TEXT DEFAULT 'card',
            receipt_file_id TEXT,
            status TEXT DEFAULT 'pending',
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # ================== جدول withdraw_requests ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdraw_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            wallet_address TEXT,
            status TEXT DEFAULT 'pending',
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # ================== جدول daily_interest_history ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_interest_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # ================== جدول tickets (پشتیبانی) ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            first_name TEXT,
            message TEXT,
            answer TEXT,
            status TEXT DEFAULT 'open',
            admin_answer TEXT,
            admin_answered_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # ================== جدول spin_items (گردونه شانس) ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spin_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            chance INTEGER NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ================== جدول referrals (رفرال) ==================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referred_id INTEGER UNIQUE NOT NULL,
            reward_amount INTEGER DEFAULT 0,
            reward_type TEXT DEFAULT 'balance',
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (referrer_id) REFERENCES users (user_id),
            FOREIGN KEY (referred_id) REFERENCES users (user_id)
        )
    ''')
    
    # ================== اضافه کردن تنظیمات پیش‌فرض ==================
    for key, value in DEFAULT_SETTINGS.items():
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
        ''', (key, value))
    
    # ================== اضافه کردن ادمین اصلی ==================
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, is_admin) VALUES (?, ?)
    ''', (ADMIN_ID, 1))
    
    conn.commit()
    conn.close()
    
    print("✅ دیتابیس با موفقیت ساخته شد!")
    print("✅ تمام جدول‌ها ایجاد شدند!")
    print("✅ جدول referrals (رفرال) ایجاد شد!")
    print("⚠️ گردونه شانس خالی است! لطفاً از پنل ادمین آیتم اضافه کن.")
    print("⚠️ هیچ محصولی وجود ندارد! لطفاً از پنل ادمین محصول اضافه کن.")


# ================== تابع آپدیت دیتابیس ==================
def update_database():
    """آپدیت دیتابیس بدون از دست دادن اطلاعات"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ===== بررسی و اضافه کردن ستون‌های جدید به جدول users =====
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [col["name"] for col in cursor.fetchall()]
    
    new_user_columns = {
        "spin_count": "INTEGER DEFAULT 0",
        "last_spin_date": "TEXT",
        "last_spin_order_id": "INTEGER DEFAULT 0",
        "referral_code": "TEXT UNIQUE",
        "referral_count": "INTEGER DEFAULT 0",
        "referral_discount": "INTEGER DEFAULT 0",
        "referred_by": "INTEGER DEFAULT 0"
    }
    
    for col_name, col_type in new_user_columns.items():
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"✅ ستون {col_name} به جدول users اضافه شد")
            except sqlite3.OperationalError as e:
                print(f"⚠️ خطا در افزودن ستون {col_name}: {e}")
    
    # ===== بررسی و اضافه کردن ستون‌های جدید به جدول orders =====
    cursor.execute("PRAGMA table_info(orders)")
    existing_columns = [col["name"] for col in cursor.fetchall()]
    
    new_order_columns = {
        "user_count": "INTEGER DEFAULT 1",
        "user_count_price": "INTEGER DEFAULT 0"
    }
    
    for col_name, col_type in new_order_columns.items():
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_type}")
                print(f"✅ ستون {col_name} به جدول orders اضافه شد")
            except sqlite3.OperationalError as e:
                print(f"⚠️ خطا در افزودن ستون {col_name}: {e}")
    
    # ===== بررسی و آپدیت جدول tickets =====
    cursor.execute("PRAGMA table_info(tickets)")
    existing_columns = [col["name"] for col in cursor.fetchall()]
    
    new_ticket_columns = {
        "username": "TEXT",
        "first_name": "TEXT",
        "admin_answer": "TEXT",
        "admin_answered_at": "TIMESTAMP"
    }
    
    for col_name, col_type in new_ticket_columns.items():
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE tickets ADD COLUMN {col_name} {col_type}")
                print(f"✅ ستون {col_name} به جدول tickets اضافه شد")
            except sqlite3.OperationalError as e:
                print(f"⚠️ خطا در افزودن ستون {col_name}: {e}")
    
    # ===== اضافه کردن تنظیمات جدید به جدول settings =====
    new_settings = {
        "bot_status": "on",
        "shop_status": "open",
        "deposit_rial": "on",
        "deposit_crypto": "on",
        "start_text": "✨ 🎉 <b>به ربات فروش کانفیگ آلفا پینگ خوش اومدی!</b> 🎉\n\n👋 سلام <code>{display_name}</code>\n\n💎 <b>اینجا میتونی با بهترین کیفیت و قیمت، وی‌پی‌ان بخری</b>\n\n⚡ سرعت بالا ⚡\n📞 پشتیبانی 24/7 📞\n✅ ضمانت بازگشت وجه (در صورت قطعی سرویس و برطرف نشدن مشکل آن) ✅\n\n🔽 <b>از منوی زیر یکی رو انتخاب کن</b> 🔽",
        "rules_text": "⚜️ <b>قوانین و مقررات ربات</b>\n\n👍 <b>اولین قانون:</b> ارسال رسید فیک ممنوع می باشد و موجب مسدود شدن سرویس های قبلی شما میگردد\n👍 <b>دومین قانون:</b> کانفیگ های آلفا پینگ صرفا برای مصرف شخصی می باشند\n👍 <b>سومین قانون:</b> هرگونه نوع مصرف بر عهده خود کاربر می باشد\n👍 <b>چهارمین قانون:</b> بازگشت وجه و یا تغییر سرویس به هیچ وجه میسر نمی باشد\n👍 <b>پنجمین قانون:</b> هرگونه تخلف = مسدودیت دائمی\n👍 <b>ششمین قانون:</b> در پنل عمده خرید کمتر از 100 گیگ میسر نمی باشد\n\n🫥 <b>با رعایت قوانین، همیشه بهترین خدمات رو دریافت کن</b>",
        "support_text": "🎧 <b>پشتیبانی ربات</b> 🎧\n\n❤️ سلام! من اینجام تا کمک کنم\nمن یه رباتم ولی تیم پشتیبانی پشت صحنه داریم 😀\n\nچطور میتونم کمکت کنم؟ 😄\n• مشکل در خرید داری؟\n• کیف پولت شارژ نمیشه؟\n• کانفیگ دریافت نکردی؟\n• یا هر سوال دیگه‌ای...\n\n🖥 <b>راه‌های ارتباطی:</b>\n@Mortaabet ✅\n\n‼️ <b>نکته:</b> قبل از پیام دادن، مشکلت رو دقیق بگو تا سریعتر حل بشه!\n\n✔️ <b>میانگین زمان پاسخ:</b> کمتر از 30 دقیقه",
        "force_join_channel": "",
        "force_join_name": "",
        "referral_enabled": "on",
        "referral_reward_type": "balance",
        "referral_reward_amount": "5000",
        "referral_discount_percent": "10",
        "referral_min_purchase": "0",
        "referral_require_purchase": "on"
    }
    
    for key, value in new_settings.items():
        cursor.execute('''
            INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
        ''', (key, value))
        print(f"✅ تنظیم {key} اضافه شد")
    
    # ===== بررسی وجود جدول spin_items =====
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='spin_items'")
    if not cursor.fetchone():
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS spin_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                chance INTEGER NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ جدول spin_items ساخته شد")
    
    # ===== بررسی وجود جدول referrals =====
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='referrals'")
    if not cursor.fetchone():
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER NOT NULL,
                referred_id INTEGER UNIQUE NOT NULL,
                reward_amount INTEGER DEFAULT 0,
                reward_type TEXT DEFAULT 'balance',
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                FOREIGN KEY (referred_id) REFERENCES users (user_id)
            )
        ''')
        print("✅ جدول referrals ساخته شد")
    
    conn.commit()
    conn.close()
    
    print("\n✅ آپدیت دیتابیس با موفقیت انجام شد!")


# ================== توابع کمکی ==================

def get_setting(key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result["value"] if result else None

def set_setting(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_user(user_id):
    """دریافت اطلاعات کاربر"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_user_balance(user_id, amount):
    """به‌روزرسانی موجودی کاربر"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    """دریافت موجودی کاربر"""
    user = get_user(user_id)
    return user["balance"] if user else 0

def add_admin_log(admin_id, action, target_user_id=None, details=None):
    """ثبت لاگ ادمین"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO admin_logs (admin_id, action, target_user_id, details)
        VALUES (?, ?, ?, ?)
    ''', (admin_id, action, target_user_id, details))
    conn.commit()
    conn.close()

def get_pending_orders():
    """دریافت سفارشات در انتظار"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, u.username, u.first_name 
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        WHERE o.status = 'pending'
        ORDER BY o.created_at DESC
    """)
    results = cursor.fetchall()
    conn.close()
    return results

def get_pending_transactions():
    """دریافت تراکنش‌های در انتظار"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, u.username, u.first_name 
        FROM transactions t
        JOIN users u ON t.user_id = u.user_id
        WHERE t.status = 'pending'
        ORDER BY t.created_at DESC
    """)
    results = cursor.fetchall()
    conn.close()
    return results


# ================== توابع مربوط به گردونه شانس ==================

def get_spin_items():
    """دریافت لیست آیتم‌های گردونه از دیتابیس"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spin_items WHERE is_active = 1 ORDER BY id")
    items = cursor.fetchall()
    conn.close()
    return items

def get_all_spin_items():
    """دریافت همه آیتم‌های گردونه (حتی غیرفعال)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spin_items ORDER BY id")
    items = cursor.fetchall()
    conn.close()
    return items

def get_spin_item_by_id(item_id):
    """دریافت یک آیتم خاص از گردونه"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spin_items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return item

def add_spin_item(name, chance, description):
    """افزودن آیتم جدید به گردونه"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO spin_items (name, chance, description, is_active)
        VALUES (?, ?, ?, 1)
    ''', (name, chance, description))
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return item_id

def update_spin_item(item_id, name, chance, description, is_active):
    """ویرایش آیتم گردونه"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE spin_items 
        SET name = ?, chance = ?, description = ?, is_active = ?
        WHERE id = ?
    ''', (name, chance, description, is_active, item_id))
    conn.commit()
    conn.close()

def delete_spin_item(item_id):
    """حذف آیتم از گردونه"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM spin_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def toggle_spin_item_status(item_id):
    """تغییر وضعیت فعال/غیرفعال آیتم گردونه"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_active FROM spin_items WHERE id = ?", (item_id,))
    result = cursor.fetchone()
    if result:
        new_status = 0 if result["is_active"] else 1
        cursor.execute("UPDATE spin_items SET is_active = ? WHERE id = ?", (new_status, item_id))
        conn.commit()
    conn.close()

def get_total_chance():
    """محاسبه مجموع درصدهای آیتم‌های فعال"""
    items = get_spin_items()
    total = sum(item["chance"] for item in items)
    return total


# ================== توابع مربوط به خرید و گردونه ==================

def has_completed_order(user_id):
    """بررسی اینکه کاربر حداقل یک سفارش تکمیل شده داره"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = 'completed'", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def get_last_completed_order_id(user_id):
    """دریافت آخرین سفارش تکمیل شده کاربر"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM orders 
        WHERE user_id = ? AND status = 'completed' 
        ORDER BY created_at DESC 
        LIMIT 1
    """, (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result["id"] if result else None

def get_last_spin_order_id(user_id):
    """دریافت آخرین سفارشی که برای آن چرخش انجام شده"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT last_spin_order_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result["last_spin_order_id"] if result else None

def can_user_spin(user_id):
    """بررسی اینکه کاربر برای آخرین خرید خود چرخش داشته یا نه"""
    last_order_id = get_last_completed_order_id(user_id)
    if not last_order_id:
        return False
    
    last_spin_order_id = get_last_spin_order_id(user_id)
    
    return last_spin_order_id is None or last_order_id > last_spin_order_id

def mark_spin_for_order(user_id, order_id):
    """ثبت چرخش برای یک سفارش خاص"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users 
        SET last_spin_order_id = ?,
            spin_count = COALESCE(spin_count, 0) + 1,
            last_spin_date = ?
        WHERE user_id = ?
    ''', (order_id, datetime.now().date().isoformat(), user_id))
    conn.commit()
    conn.close()

def get_user_spin_count(user_id):
    """دریافت تعداد کل چرخش‌های کاربر"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT spin_count FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result["spin_count"] if result else 0

def reset_daily_spins():
    """این تابع دیگه استفاده نمیشه - برای سازگاری نگه داشته شده"""
    pass


# ================== توابع مربوط به تیکت‌ها ==================

def create_ticket(user_id, username, first_name, message):
    """ایجاد تیکت جدید"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tickets (user_id, username, first_name, message, status)
        VALUES (?, ?, ?, ?, 'open')
    ''', (user_id, username, first_name, message))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    return ticket_id

def get_user_tickets(user_id):
    """دریافت تیکت‌های یک کاربر"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM tickets 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    ''', (user_id,))
    tickets = cursor.fetchall()
    conn.close()
    return tickets

def get_all_tickets():
    """دریافت همه تیکت‌ها برای ادمین"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(tickets)")
        columns = [col["name"] for col in cursor.fetchall()]
        
        if "created_at" in columns:
            cursor.execute('''
                SELECT * FROM tickets 
                ORDER BY 
                    CASE 
                        WHEN status = 'open' THEN 0
                        WHEN status = 'answered' THEN 1
                        WHEN status = 'closed' THEN 2
                    END,
                    created_at DESC
            ''')
        else:
            cursor.execute('''
                SELECT * FROM tickets 
                ORDER BY 
                    CASE 
                        WHEN status = 'open' THEN 0
                        WHEN status = 'answered' THEN 1
                        WHEN status = 'closed' THEN 2
                    END,
                    id DESC
            ''')
    except:
        cursor.execute("SELECT * FROM tickets ORDER BY id DESC")
    
    tickets = cursor.fetchall()
    conn.close()
    return tickets

def get_ticket_by_id(ticket_id):
    """دریافت تیکت با آیدی"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    ticket = cursor.fetchone()
    conn.close()
    return ticket

def answer_ticket(ticket_id, admin_answer, admin_id):
    """پاسخ دادن به تیکت توسط ادمین"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE tickets 
        SET admin_answer = ?, 
            admin_answered_at = CURRENT_TIMESTAMP,
            status = 'answered'
        WHERE id = ?
    ''', (admin_answer, ticket_id))
    conn.commit()
    conn.close()

def close_ticket(ticket_id):
    """بستن تیکت"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET status = 'closed' WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()

def delete_ticket(ticket_id):
    """حذف تیکت"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()

def get_open_tickets_count():
    """دریافت تعداد تیکت‌های باز"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ================== توابع مربوط به مدیریت ادمین‌ها ==================

def get_all_admins():
    """دریافت لیست همه ادمین‌ها"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, first_name, username FROM users WHERE is_admin = 1")
    admins = cursor.fetchall()
    conn.close()
    return admins

def add_admin(user_id):
    """افزودن ادمین جدید"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def remove_admin(user_id):
    """حذف ادمین (فقط برای غیر از ادمین اصلی)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_admin = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def is_user_admin(user_id):
    """بررسی اینکه کاربر ادمین هست یا نه"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result["is_admin"] == 1 if result else False


# ================== توابع مربوط به رفرال ==================

def get_referral_settings():
    """دریافت تنظیمات رفرال"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM settings WHERE key LIKE 'referral_%'")
    settings = cursor.fetchall()
    conn.close()
    
    result = {
        "enabled": "on",
        "reward_type": "balance",
        "reward_amount": 5000,
        "discount_percent": 10,
        "min_purchase": 0,
        "require_purchase": "on"
    }
    
    for setting in settings:
        key = setting["key"].replace("referral_", "")
        if key == "enabled":
            result["enabled"] = setting["value"]
        elif key == "reward_type":
            result["reward_type"] = setting["value"]
        elif key == "reward_amount":
            result["reward_amount"] = int(setting["value"]) if setting["value"] else 0
        elif key == "discount_percent":
            result["discount_percent"] = int(setting["value"]) if setting["value"] else 0
        elif key == "min_purchase":
            result["min_purchase"] = int(setting["value"]) if setting["value"] else 0
        elif key == "require_purchase":
            result["require_purchase"] = setting["value"] if setting["value"] else "on"
    
    return result

def set_referral_setting(key, value):
    """تنظیم تنظیمات رفرال"""
    set_setting(f"referral_{key}", str(value))

def generate_referral_code(user_id):
    """تولید کد رفرال یکتا برای کاربر"""
    import hashlib
    import base64
    
    salt = "alpha_ping_ref"
    combined = f"{salt}_{user_id}_{datetime.now().timestamp()}"
    hash_obj = hashlib.sha256(combined.encode())
    code = base64.urlsafe_b64encode(hash_obj.digest()[:8]).decode().replace("-", "").replace("_", "")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE referral_code = ?", (code,))
    existing = cursor.fetchone()
    conn.close()
    
    if existing:
        return generate_referral_code(user_id)
    
    return code

def get_or_create_referral_code(user_id):
    """دریافت یا ایجاد کد رفرال برای کاربر"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT referral_code FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result and result["referral_code"]:
        code = result["referral_code"]
        conn.close()
        return code
    
    code = generate_referral_code(user_id)
    cursor.execute("UPDATE users SET referral_code = ? WHERE user_id = ?", (code, user_id))
    conn.commit()
    conn.close()
    return code

def get_user_by_referral_code(code):
    """دریافت کاربر با کد رفرال"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE referral_code = ?", (code,))
    result = cursor.fetchone()
    conn.close()
    return result["user_id"] if result else None

def register_referral(referrer_id, referred_id):
    """ثبت رفرال جدید و اعمال پاداش فوری در صورت فعال بودن"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # بررسی اینکه قبلاً ثبت نشده باشد
    cursor.execute("SELECT id FROM referrals WHERE referred_id = ?", (referred_id,))
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return False
    
    settings = get_referral_settings()
    
    # ثبت رفرال
    cursor.execute('''
        INSERT INTO referrals (referrer_id, referred_id, status)
        VALUES (?, ?, 'pending')
    ''', (referrer_id, referred_id))
    
    # ذخیره referred_by در جدول users
    cursor.execute('''
        UPDATE users SET referred_by = ? WHERE user_id = ?
    ''', (referrer_id, referred_id))
    
    # ===== اگر حالت فوری فعال باشد (require_purchase = off) =====
    if settings["enabled"] == "on" and settings["require_purchase"] == "off":
        # اعمال پاداش فوری
        if settings["reward_type"] == "balance":
            reward = settings["reward_amount"]
            
            # به‌روزرسانی موجودی کاربر دعوت‌کننده
            cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, referrer_id))
            
            # ثبت در تراکنش‌ها
            cursor.execute('''
                INSERT INTO transactions (user_id, amount, currency_type, proof, status)
                VALUES (?, ?, 'referral', ?, 'approved')
            ''', (referrer_id, reward, f"پاداش فوری رفرال برای کاربر {referred_id}"))
            
        elif settings["reward_type"] == "discount":
            discount = settings["discount_percent"]
            cursor.execute('''
                UPDATE users SET referral_discount = ? WHERE user_id = ?
            ''', (discount, referrer_id))
        
        # به‌روزرسانی وضعیت رفرال به completed
        cursor.execute('''
            UPDATE referrals 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE referred_id = ?
        ''', (referred_id,))
        
        # افزایش تعداد رفرال‌ها
        cursor.execute('''
            UPDATE users SET referral_count = COALESCE(referral_count, 0) + 1 
            WHERE user_id = ?
        ''', (referrer_id,))
    
    conn.commit()
    conn.close()
    return True

def complete_referral(referred_id):
    """تکمیل رفرال پس از اولین خرید (فقط در حالت نیاز به خرید)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    settings = get_referral_settings()
    
    # اگر حالت فوری فعال باشد، نیازی به تکمیل نیست
    if settings["require_purchase"] == "off":
        conn.close()
        return True
    
    # پیدا کردن رفرال در انتظار
    cursor.execute('''
        SELECT id, referrer_id FROM referrals 
        WHERE referred_id = ? AND status = 'pending'
    ''', (referred_id,))
    referral = cursor.fetchone()
    
    if not referral:
        conn.close()
        return False
    
    if settings["enabled"] != "on":
        conn.close()
        return False
    
    referrer_id = referral["referrer_id"]
    
    # اعمال پاداش
    if settings["reward_type"] == "balance":
        reward = settings["reward_amount"]
        
        # به‌روزرسانی موجودی کاربر دعوت‌کننده
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (reward, referrer_id))
        
        # ثبت در تراکنش‌ها
        cursor.execute('''
            INSERT INTO transactions (user_id, amount, currency_type, proof, status)
            VALUES (?, ?, 'referral', ?, 'approved')
        ''', (referrer_id, reward, f"پاداش رفرال برای کاربر {referred_id}"))
        
    elif settings["reward_type"] == "discount":
        discount = settings["discount_percent"]
        cursor.execute('''
            UPDATE users SET referral_discount = ? WHERE user_id = ?
        ''', (discount, referrer_id))
    
    # به‌روزرسانی وضعیت رفرال
    cursor.execute('''
        UPDATE referrals 
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (referral["id"],))
    
    # افزایش تعداد رفرال‌ها
    cursor.execute('''
        UPDATE users SET referral_count = COALESCE(referral_count, 0) + 1 
        WHERE user_id = ?
    ''', (referrer_id,))
    
    conn.commit()
    conn.close()
    return True

def get_referral_stats(user_id):
    """دریافت آمار رفرال‌های کاربر"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
        FROM referrals WHERE referrer_id = ?
    ''', (user_id,))
    stats = cursor.fetchone()
    
    cursor.execute('''
        SELECT reward_amount, created_at, status
        FROM referrals WHERE referrer_id = ?
        ORDER BY created_at DESC LIMIT 10
    ''', (user_id,))
    recent = cursor.fetchall()
    
    conn.close()
    
    return {
        "total": stats["total"] or 0,
        "pending": stats["pending"] or 0,
        "completed": stats["completed"] or 0,
        "recent": recent
    }

def get_referral_discount(user_id):
    """دریافت تخفیف رفرال کاربر"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT referral_discount FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result["referral_discount"] if result else 0

def use_referral_discount(user_id):
    """استفاده از تخفیف رفرال و صفر کردن آن"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET referral_discount = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_top_referrers(limit=10):
    """دریافت کاربران با بیشترین رفرال"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.user_id, u.first_name, u.username, 
               COUNT(r.id) as referral_count,
               SUM(CASE WHEN r.status = 'completed' THEN 1 ELSE 0 END) as completed_count
        FROM users u
        LEFT JOIN referrals r ON u.user_id = r.referrer_id
        GROUP BY u.user_id
        ORDER BY completed_count DESC
        LIMIT ?
    ''', (limit,))
    results = cursor.fetchall()
    conn.close()
    return results


# ================== اجرای آپدیت ==================
if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        print("🔄 دیتابیس موجود است. در حال آپدیت...")
        update_database()
    else:
        print("🆕 دیتابیس وجود ندارد. در حال ساخت...")
        init_database()
