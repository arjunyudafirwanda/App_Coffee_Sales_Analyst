from sqlalchemy import text
from db_config import get_engine
import hashlib

# 🔐 Hash password dengan SHA256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ✅ Verifikasi password input dengan hashed password di DB
def verify_password(plain_password, hashed_password):
    return hash_password(plain_password) == hashed_password

# 🔎 Ambil hashed password berdasarkan username
def get_user_hashed_password(username):
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(
            text("SELECT password FROM users WHERE username = :username"),
            {"username": username}
        )
        row = result.fetchone()
        return row[0] if row else None

def verify_login(username, password):
    engine = get_engine()
    query = text("SELECT id, username, password, role FROM users WHERE username = :username")
    with engine.connect() as conn:
        result = conn.execute(query, {"username": username}).mappings().first()
        if result:
            hashed_input = hashlib.sha256(password.encode()).hexdigest()
            if result["password"] == hashed_input:
                return {
                    "id": result["id"], 
                    "username": result["username"],
                    "role": result["role"]
                    }
    return None


# 📝 Fungsi untuk registrasi user baru
def register_user(username, password):
    engine = get_engine()
    hashed = hash_password(password)
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO users (username, password) VALUES (:username, :password)"),
            {"username": username, "password": hashed}
        )

# 🔁 Ganti password
def change_password(username, new_password):
    engine = get_engine()
    hashed = hash_password(new_password)
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET password = :password WHERE username = :username"),
            {"password": hashed, "username": username}
        )
