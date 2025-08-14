from sqlalchemy import create_engine, text

def get_engine():
    user = 'root'
    password = ''
    host = 'localhost'
    database = 'coffee_db'

    engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
    return engine

def test_connection():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Koneksi berhasil:", result.scalar())
    except Exception as e:
        print("❌ Gagal konek:", e)

# Tes koneksi
if __name__ == "__main__":
    test_connection()
