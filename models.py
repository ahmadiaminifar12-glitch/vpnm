from database import get_db_connection

class User:
    @staticmethod
    def get_or_create(user_id, username, first_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)
            ''', (user_id, username, first_name))
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
        
        conn.close()
        return user
    
    @staticmethod
    def get_balance(user_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result["balance"] if result else 0
    
    @staticmethod
    def update_balance(user_id, new_balance):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = ? WHERE user_id = ?", (new_balance, user_id))
        conn.commit()
        conn.close()

class Order:
    @staticmethod
    def create(user_id, server, volume, duration, total_price):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (user_id, server, volume, duration, total_price, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        ''', (user_id, server, volume, duration, total_price))
        conn.commit()
        order_id = cursor.lastrowid
        conn.close()
        return order_id
    
    @staticmethod
    def get_pending_orders():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE status = 'pending' ORDER BY id DESC")
        orders = cursor.fetchall()
        conn.close()
        return orders

class Product:
    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY id")
        products = cursor.fetchall()
        conn.close()
        return products
    
    @staticmethod
    def get_by_id(product_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
        product = cursor.fetchone()
        conn.close()
        return product
    
    @staticmethod
    def create(name, price_per_gb, button_color):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO products (name, price_per_gb, button_color, is_active)
            VALUES (?, ?, ?, 1)
        ''', (name, price_per_gb, button_color))
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        return product_id
    
    @staticmethod
    def update(product_id, name, price_per_gb, button_color, is_active):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE products 
            SET name = ?, price_per_gb = ?, button_color = ?, is_active = ?
            WHERE id = ?
        ''', (name, price_per_gb, button_color, is_active, product_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete(product_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()