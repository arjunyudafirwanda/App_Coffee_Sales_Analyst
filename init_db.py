# DELETE FROM users;
# ALTER TABLE users AUTO_INCREMENT = 1;


from db_config import get_engine
from sqlalchemy import text
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

engine = get_engine()

with engine.begin() as conn:
    # Buat tabel users
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user'
        )
    """))

    # Tambahkan admin default (username: admin, password: admin123)
    admin_username = 'admin'
    admin_password = hash_password('admin123')
    admin_role = 'admin'

    # Cek apakah admin sudah ada
    result = conn.execute(text("SELECT * FROM users WHERE username = :username"), {"username": admin_username})
    if not result.fetchone():
        conn.execute(text("""
            INSERT INTO users (username, password, role)
            VALUES (:username, :password, :role)
        """), {"username": admin_username, "password": admin_password, "role": admin_role})
        print("✅ Admin user berhasil ditambahkan.")
    else:
        print("ℹ️ Admin user sudah ada, tidak ditambahkan ulang.")
