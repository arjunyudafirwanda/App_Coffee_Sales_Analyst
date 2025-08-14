from sqlalchemy import create_engine, text

# Ganti sesuai koneksi database Anda
engine = create_engine("mysql+mysqlconnector://root:@localhost/coffee_db")

# Eksekusi insert untuk testing
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO users (username, password, role) VALUES (:u, :p, :r)"), 
        {"u": "tes_user", "p": "123abc", "r": "user"}
    )
    print("✅ Data berhasil masuk")
