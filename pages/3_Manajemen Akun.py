import time
import streamlit as st
from sqlalchemy import text
from db_config import get_engine
from utils import protect_page, hash_password

# Proteksi halaman (hanya bisa diakses jika login)
protect_page()

# Hanya admin yang bisa akses
if st.session_state.get("role") != "admin":
    st.warning("⚠️ Halaman ini hanya bisa diakses oleh admin.")
    st.stop()

st.set_page_config(page_title="👤 Manajemen Akun", layout="wide")
st.title("👤 Manajemen Akun Pengguna")

# Informasi profil
role = st.session_state.get("role", "user")
username = st.session_state.get("username", "User")

engine = get_engine()

# === Load akun dari database ===
def load_users():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT username, role FROM users ORDER BY username"))
        return result.fetchall()

users = load_users()

# === Tampilkan Daftar Akun ===
if not users:
    st.info("Belum ada akun yang terdaftar.")
else:
    st.markdown("### 📋 Daftar Akun Terdaftar")
    for user in users:
        st.markdown(f"- **{user.username}** — `Role: {user.role}`")

    st.markdown("### 🗑️ Hapus Akun")
    user_list = [user.username for user in users]
    selected_user = st.selectbox("Pilih akun yang ingin dihapus:", user_list)

    if selected_user != "admin":
        if st.button(f"Hapus Akun '{selected_user}'"):
            st.session_state.hapus_ditekan = True

    if st.session_state.get("hapus_ditekan"):
        confirm = st.checkbox("Saya yakin ingin menghapus akun ini secara permanen.")
        if confirm:
            if selected_user == st.session_state.get("username"):
                st.warning("⚠️ Tidak dapat menghapus akun yang sedang digunakan.")
            else:
                try:
                    with engine.begin() as conn:
                        conn.execute(text("DELETE FROM users WHERE username = :u"), {"u": selected_user})
                    st.success(f"✅ Akun '{selected_user}' berhasil dihapus.")
                    st.session_state.hapus_ditekan = False
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Gagal menghapus akun: {e}")

# === Tambah Akun Baru ===
st.markdown("---")
st.markdown("### ➕ Tambah Akun Baru")

# Reset input form jika perlu
if st.session_state.get("reset_form", False):
    st.session_state.input_username = ""
    st.session_state.input_password = ""
    st.session_state.input_role = "user"
    st.session_state.reset_form = False

new_username = st.text_input("Username Baru", key="input_username")
new_password = st.text_input("Password Baru", type="password", key="input_password")
new_role = st.selectbox("Role", ["user", "admin"], key="input_role")

if st.button("Tambah Akun"):
    if len(new_username) < 3 or len(new_password) < 6:
        st.warning("⚠️ Username atau password terlalu pendek (min 3 dan 6 karakter).")
    else:
        hashed_pw = hash_password(new_password)
        try:
            with engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO users (username, password, role)
                        VALUES (:u, :p, :r)
                    """),
                    {"u": new_username, "p": hashed_pw, "r": new_role}
                )
            st.success(f"✅ Akun '{new_username}' berhasil ditambahkan.")
            st.session_state.reset_form = True
            time.sleep(2)
            st.rerun()
        except Exception as e:
            if "Duplicate entry" in str(e):
                st.warning("⚠️ Username sudah ada di database.")
            else:
                st.error(f"❌ Gagal menambahkan akun: {e}")

# === Edit Role Pengguna ===
st.markdown("---")
st.markdown("### ✏️ Edit Role Pengguna")

edit_user = st.selectbox("Pilih akun untuk diedit rolenya:", user_list, key="edit_user_selectbox")
if edit_user == "admin":
    st.info("Akun 'admin' default tidak bisa diedit.")
else:
    with engine.connect() as conn:
        current_role = conn.execute(text("SELECT role FROM users WHERE username = :u"), {"u": edit_user}).scalar()

    new_role = st.selectbox("Pilih Role Baru:", ["user", "admin"], index=["user", "admin"].index(current_role))

    if new_role == current_role:
        st.info("Role saat ini sudah sesuai.")
    else:
        if st.button("Update Role"):
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text("UPDATE users SET role = :r WHERE username = :u"),
                        {"r": new_role, "u": edit_user}
                    )
                st.success(f"✅ Role untuk '{edit_user}' berhasil diubah menjadi '{new_role}'.")
                time.sleep(2)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Gagal mengubah role: {e}")

# === Profil Sidebar ===
with st.sidebar:
    st.markdown("### 👤 Profil")
    st.markdown(f"**{username.title()}**")
    st.markdown(f"Role: `{role}`")

# === Tombol Logout ===
with st.sidebar:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("Dashboard_Analisis_Penjualan_Kopi.py")
        
# === Footer ===
st.markdown("---")
st.caption("© 2025 Coffee Shop Analyst Dashboard Created By Arjun Yuda Firwanda")
