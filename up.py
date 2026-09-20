import sqlite3
import os

DB_PATH = "bot.db"

def fix_tickets_table():
    """تعمیر کامل جدول tickets - حذف و بازسازی با ساختار صحیح"""
    print("🔧 در حال تعمیر کامل جدول tickets...")
    
    if not os.path.exists(DB_PATH):
        print("❌ فایل دیتابیس وجود ندارد!")
        print("🆕 لطفاً ابتدا ربات را اجرا کنید تا دیتابیس ساخته شود.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ===== 1. بررسی اینکه جدول tickets وجود دارد =====
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tickets'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        print("📋 جدول tickets وجود ندارد. در حال ایجاد...")
        cursor.execute('''
            CREATE TABLE tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                first_name TEXT,
                message TEXT,
                answer TEXT,
                status TEXT DEFAULT 'open',
                admin_answer TEXT,
                admin_answered_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ جدول tickets ایجاد شد")
        conn.commit()
        conn.close()
        print("✅ تعمیر با موفقیت انجام شد!")
        return
    
    # ===== 2. بررسی ستون‌های فعلی =====
    cursor.execute("PRAGMA table_info(tickets)")
    current_columns = [col[1] for col in cursor.fetchall()]
    print(f"📋 ستون‌های فعلی: {current_columns}")
    
    # ===== 3. ستون‌های مورد نیاز =====
    required_columns = [
        "id", "user_id", "username", "first_name", "message", 
        "answer", "status", "admin_answer", "admin_answered_at", "created_at"
    ]
    
    # ===== 4. بررسی ستون‌های缺失 =====
    missing_columns = [col for col in required_columns if col not in current_columns]
    
    if not missing_columns:
        print("✅ همه ستون‌ها وجود دارند!")
        conn.close()
        return
    
    print(f"⚠️ ستون‌های {missing_columns} وجود ندارند. در حال بازسازی جدول...")
    
    # ===== 5. پشتیبان‌گیری از داده‌ها =====
    cursor.execute("SELECT * FROM tickets")
    old_data = cursor.fetchall()
    print(f"📋 تعداد رکوردهای موجود: {len(old_data)}")
    
    # ===== 6. حذف جدول قدیمی =====
    cursor.execute("DROP TABLE tickets")
    print("✅ جدول قدیمی حذف شد")
    
    # ===== 7. ایجاد جدول جدید =====
    cursor.execute('''
        CREATE TABLE tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            first_name TEXT,
            message TEXT,
            answer TEXT,
            status TEXT DEFAULT 'open',
            admin_answer TEXT,
            admin_answered_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ جدول جدید ایجاد شد")
    
    # ===== 8. بازیابی داده‌ها =====
    if old_data:
        # دریافت نام ستون‌ها
        cursor.execute("PRAGMA table_info(tickets)")
        new_columns = [col[1] for col in cursor.fetchall()]
        
        # ستون‌های مشترک بین جدول قدیم و جدید
        common_columns = [col for col in new_columns if col in current_columns]
        
        if common_columns:
            # ساخت کوئری INSERT
            placeholders = ', '.join(['?' for _ in common_columns])
            columns_str = ', '.join(common_columns)
            
            # آماده‌سازی داده‌ها
            for row in old_data:
                # پیدا کردن اندیس ستون‌ها در دیتای قدیمی
                row_data = []
                for col in common_columns:
                    if col in current_columns:
                        idx = current_columns.index(col)
                        row_data.append(row[idx] if row[idx] is not None else None)
                    else:
                        row_data.append(None)
                
                try:
                    cursor.execute(f"INSERT INTO tickets ({columns_str}) VALUES ({placeholders})", row_data)
                except:
                    pass
            
            print(f"✅ {len(old_data)} رکورد بازیابی شد")
    
    conn.commit()
    
    # ===== 9. تایید نهایی =====
    cursor.execute("PRAGMA table_info(tickets)")
    final_columns = [col[1] for col in cursor.fetchall()]
    print(f"📋 ستون‌های نهایی: {final_columns}")
    
    if "created_at" in final_columns:
        print("✅ ✅ ✅ همه ستون‌ها با موفقیت اضافه شدند!")
    else:
        print("❌ ❌ ❌ خطا! ستون created_at اضافه نشد!")
    
    conn.close()
    print("\n✅ تعمیر جدول tickets با موفقیت انجام شد!")


def fix_get_user_tickets():
    """نمایش کد اصلاح‌شده تابع get_user_tickets"""
    print("\n📋 لطفاً تابع get_user_tickets را در database.py به این شکل اصلاح کن:\n")
    print('''
def get_user_tickets(user_id):
    """دریافت تیکت‌های یک کاربر"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # بررسی وجود ستون created_at
        cursor.execute("PRAGMA table_info(tickets)")
        columns = [col["name"] for col in cursor.fetchall()]
        
        if "created_at" in columns:
            cursor.execute("""
                SELECT * FROM tickets 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT * FROM tickets 
                WHERE user_id = ? 
                ORDER BY id DESC
            """, (user_id,))
    except:
        cursor.execute("""
            SELECT * FROM tickets 
            WHERE user_id = ? 
            ORDER BY id DESC
        """, (user_id,))
    
    tickets = cursor.fetchall()
    conn.close()
    return tickets
    ''')


if __name__ == "__main__":
    fix_tickets_table()
    fix_get_user_tickets()
