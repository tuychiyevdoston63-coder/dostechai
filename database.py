import sqlite3
from datetime import datetime
from config import DATABASE_NAME

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                registered_at TEXT
            )
        ''')
        
        # Products table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                name TEXT,
                photo_id TEXT,
                short_description TEXT,
                full_description TEXT,
                features TEXT,
                price TEXT,
                demo_url TEXT,
                status TEXT DEFAULT 'available',
                created_at TEXT
            )
        ''')
        
        # Orders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                project_type TEXT,
                description TEXT,
                features TEXT,
                budget TEXT,
                deadline TEXT,
                contact TEXT,
                status TEXT DEFAULT 'new',
                admin_response TEXT,
                created_at TEXT
            )
        ''')
        
        # Suggestions table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                title TEXT,
                content TEXT,
                additional_info TEXT,
                status TEXT DEFAULT 'new',
                admin_response TEXT,
                created_at TEXT
            )
        ''')
        
        # News table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                photo_id TEXT,
                content TEXT,
                created_at TEXT
            )
        ''')
        
        # Settings table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Insert default settings
        settings = [
            ('telegram_channel', 'https://t.me/dostech_ai'),
            ('telegram_contact', 'https://t.me/dostech_support'),
            ('instagram', 'https://instagram.com/dostech_ai'),
            ('website', 'https://dostech.ai'),
            ('company_name', 'DOSTECH AI')
        ]
        
        for key, value in settings:
            self.cursor.execute('''
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            ''', (key, value))
        
        self.conn.commit()
    
    # User methods
    def add_user(self, telegram_id, username, first_name, last_name):
        try:
            self.cursor.execute('''
                INSERT OR IGNORE INTO users (telegram_id, username, first_name, last_name, registered_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (telegram_id, username, first_name, last_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.conn.commit()
        except:
            pass
    
    def get_user(self, telegram_id):
        self.cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
        return self.cursor.fetchone()
    
    def get_all_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()
    
    def get_users_count(self):
        self.cursor.execute('SELECT COUNT(*) FROM users')
        return self.cursor.fetchone()[0]
    
    def update_user_phone(self, telegram_id, phone):
        self.cursor.execute('UPDATE users SET phone = ? WHERE telegram_id = ?', (phone, telegram_id))
        self.conn.commit()
    
    # Product methods
    def add_product(self, category, name, photo_id, short_desc, full_desc, features, price, demo_url, status='available'):
        self.cursor.execute('''
            INSERT INTO products (category, name, photo_id, short_description, full_description, features, price, demo_url, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (category, name, photo_id, short_desc, full_desc, features, price, demo_url, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_products_by_category(self, category):
        self.cursor.execute('SELECT * FROM products WHERE category = ?', (category,))
        return self.cursor.fetchall()
    
    def get_product(self, product_id):
        self.cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        return self.cursor.fetchone()
    
    def get_all_products(self):
        self.cursor.execute('SELECT * FROM products')
        return self.cursor.fetchall()
    
    def update_product(self, product_id, **kwargs):
        for key, value in kwargs.items():
            self.cursor.execute(f'UPDATE products SET {key} = ? WHERE id = ?', (value, product_id))
        self.conn.commit()
    
    def delete_product(self, product_id):
        self.cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
        self.conn.commit()
    
    def get_products_count(self):
        self.cursor.execute('SELECT COUNT(*) FROM products')
        return self.cursor.fetchone()[0]
    
    def get_sold_products_count(self):
        self.cursor.execute('SELECT COUNT(*) FROM products WHERE status = "sold"')
        return self.cursor.fetchone()[0]
    
    def search_products(self, query):
        self.cursor.execute('''
            SELECT * FROM products 
            WHERE name LIKE ? OR category LIKE ? OR short_description LIKE ? OR full_description LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        return self.cursor.fetchall()
    
    # Order methods
    def add_order(self, user_id, project_type, description, features, budget, deadline, contact):
        self.cursor.execute('''
            INSERT INTO orders (user_id, project_type, description, features, budget, deadline, contact, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, project_type, description, features, budget, deadline, contact, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_orders_by_user(self, user_id):
        self.cursor.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC', (user_id,))
        return self.cursor.fetchall()
    
    def get_all_orders(self):
        self.cursor.execute('SELECT * FROM orders ORDER BY id DESC')
        return self.cursor.fetchall()
    
    def get_order(self, order_id):
        self.cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
        return self.cursor.fetchone()
    
    def update_order_status(self, order_id, status, response=None):
        if response:
            self.cursor.execute('UPDATE orders SET status = ?, admin_response = ? WHERE id = ?', (status, response, order_id))
        else:
            self.cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        self.conn.commit()
    
    def get_orders_count(self):
        self.cursor.execute('SELECT COUNT(*) FROM orders')
        return self.cursor.fetchone()[0]
    
    def get_user_orders_count(self, user_id):
        self.cursor.execute('SELECT COUNT(*) FROM orders WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()[0]
    
    # Suggestion methods
    def add_suggestion(self, user_id, title, content, additional_info):
        self.cursor.execute('''
            INSERT INTO suggestions (user_id, title, content, additional_info, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, title, content, additional_info, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_suggestions(self):
        self.cursor.execute('SELECT * FROM suggestions ORDER BY id DESC')
        return self.cursor.fetchall()
    
    def get_suggestion(self, suggestion_id):
        self.cursor.execute('SELECT * FROM suggestions WHERE id = ?', (suggestion_id,))
        return self.cursor.fetchone()
    
    def update_suggestion_status(self, suggestion_id, status, response=None):
        if response:
            self.cursor.execute('UPDATE suggestions SET status = ?, admin_response = ? WHERE id = ?', (status, response, suggestion_id))
        else:
            self.cursor.execute('UPDATE suggestions SET status = ? WHERE id = ?', (status, suggestion_id))
        self.conn.commit()
    
    def get_suggestions_count(self):
        self.cursor.execute('SELECT COUNT(*) FROM suggestions')
        return self.cursor.fetchone()[0]
    
    def get_user_suggestions_count(self, user_id):
        self.cursor.execute('SELECT COUNT(*) FROM suggestions WHERE user_id = ?', (user_id,))
        return self.cursor.fetchone()[0]
    
    # News methods
    def add_news(self, title, photo_id, content):
        self.cursor.execute('''
            INSERT INTO news (title, photo_id, content, created_at)
            VALUES (?, ?, ?, ?)
        ''', (title, photo_id, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_all_news(self):
        self.cursor.execute('SELECT * FROM news ORDER BY id DESC')
        return self.cursor.fetchall()
    
    def get_news(self, news_id):
        self.cursor.execute('SELECT * FROM news WHERE id = ?', (news_id,))
        return self.cursor.fetchone()
    
    def update_news(self, news_id, title, photo_id, content):
        self.cursor.execute('UPDATE news SET title = ?, photo_id = ?, content = ? WHERE id = ?', (title, photo_id, content, news_id))
        self.conn.commit()
    
    def delete_news(self, news_id):
        self.cursor.execute('DELETE FROM news WHERE id = ?', (news_id,))
        self.conn.commit()
    
    def get_news_count(self):
        self.cursor.execute('SELECT COUNT(*) FROM news')
        return self.cursor.fetchone()[0]
    
    # Settings methods
    def get_setting(self, key):
        self.cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    
    def update_setting(self, key, value):
        self.cursor.execute('UPDATE settings SET value = ? WHERE key = ?', (value, key))
        self.conn.commit()
    
    # Statistics
    def get_statistics(self):
        stats = {
            'users': self.get_users_count(),
            'products': self.get_products_count(),
            'orders': self.get_orders_count(),
            'suggestions': self.get_suggestions_count(),
            'news': self.get_news_count(),
            'sold_products': self.get_sold_products_count()
        }
        return stats

db = Database()
