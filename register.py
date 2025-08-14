import streamlit as st
from auth.auth import hash_password
from db_config import get_engine
from sqlalchemy import text

st.set_page_config(page_title="Register", page_icon="📝")
st.title("📝 Registrasi Akun")

with st.form("register_form"):
    username = st.text_input("👤 Username", placeholder="Pilih username")
    password = st.text_input("🔑 Password", type="password", placeholder="Masukkan password")
    confirm_password = st.text_input("🔁 Konfirmasi Password", type="password", placeholder="Ulangi password")
    submitted = st.form_submit_button("Daftar")

    if submitted:
        if not username or not password or not confirm_password:
            st.warning("⚠️ Semua kolom harus diisi.")
        elif password != confirm_password:
            st.error("❌ Password tidak cocok.")
        elif len(password) < 8:
            st.error("❌ Password minimal 8 karakter.")
        else:
            engine = get_engine()
            with engine.begin() as conn:
                result = conn.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username})
                if result.fetchone():
                    st.warning("⚠️ Username sudah digunakan.")
                else:
                    hashed = hash_password(password)
                    conn.execute(
                        text("INSERT INTO users (username, password) VALUES (:username, :password)"),
                        {"username": username, "password": hashed}
                    )
                    st.success("✅ Registrasi berhasil. Silakan login.")
