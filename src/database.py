import sqlite3
import hashlib


class Database:

    SCHEMA_FILE_PATH = "schema.sql"
    DATABASE_FILE_NAME = "database.db"

    @staticmethod
    def execute(sql, params=()):
        # 1. Подключаемся к базе данных
        connection = sqlite3.connect(Database.DATABASE)

        # 2. Получаем курсор базы данных
        cursor = connection.cursor()

        # 3. Ввыполняем какой-то код...
        cursor.execute(sql, params)

        # 4. Фиксируем изменения в БД
        connection.commit()

    @staticmethod
    def select(sql,params=()):
        connection = sqlite3.connect(Database.DATABASE)
       
        cursor = connection.cursor()

        cursor.execute(sql, params)
        
        return cursor.fetchall()
        
    
    @staticmethod
    def register_user(email, phone, password):
        password_hash = hashlib.md5(password.encode()).hexdigest()
        Database.execute(
            "INSERT INTO users (email, phone, password_hash) VALUES (?, ?, ?)",
            [email, phone, password_hash]
        )

    @staticmethod
    def can_be_logged_in(email_or_phone, password):
        user = Database.find_user_by_email_or_phone(email_or_phone)
        if user is None:
            return False

        password_hash = hashlib.md5(password.encode()).hexdigest()
        real_password_hash = Database.select(
            "SELECT * FROM users WHERE email = ? OR phone = ?",
            [email_or_phone, email_or_phone]
        )[0][3]

        if password_hash != real_password_hash:
            return False
        
        return True

    @staticmethod
    def find_user_by_email_or_phone(email_or_phone):
        users = Database.select(
            "SELECT * FROM users WHERE email = ? OR phone = ?",
            [email_or_phone, email_or_phone]
        )

        if not users:
            return None
        
        id, email, phone, password_hash = users[0]
        return User(email=email, phone=phone, id=id)
