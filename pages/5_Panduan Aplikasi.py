import streamlit as st
from utils import protect_page

# Proteksi halaman (hanya bisa diakses jika login)
protect_page()

# Konfigurasi halaman
st.set_page_config(page_title="Panduan Aplikasi", page_icon="📘")

# Dapatkan data sesi (role dan username jika digunakan)
role = st.session_state.get("role", None)
username = st.session_state.get("username", "Pengguna")

# Judul halaman
st.title("📘 Panduan Penggunaan Aplikasi")

# Salam pembuka
st.markdown(f"""
Selamat datang di aplikasi **Dashboard Penjualan Kopi**!
Halaman ini berisi panduan lengkap untuk menggunakan aplikasi ini.
""")

# Panduan per fitur
st.markdown("---")
st.markdown("### 🔐 Login & Registrasi")
st.markdown("""
- Pengguna wajib login sebelum mengakses fitur aplikasi.
- Jika belum memiliki akun, silakan registrasi melalui halaman **Register**.
""")

st.markdown("### 📊 Analisis Penjualan")
st.markdown("""
- Masuk ke menu **Analisis**.
- Tampilkan grafik interaktif berdasarkan data penjualan.
- Filter berdasarkan produk, tanggal, dsb.
""")

# Tampilkan hanya jika role-nya admin
if role == "admin":
    st.markdown("### 👥 Manajemen Akun (Khusus Admin)")
    st.markdown("""
    - Tambahkan akun baru untuk admin atau user.
    - Edit data akun atau hapus akun jika diperlukan.
    """)

st.markdown("### 🔑 Ganti Password")
st.markdown("""
- Menu ini tersedia untuk semua pengguna.
- Masuk ke halaman **Ganti Password**.
- Masukkan password lama dan password baru.
- Password baru harus minimal 6 karakter.
""")

st.markdown("### 🚪 Logout")
st.markdown("""
- Gunakan tombol **Logout** pada sidebar untuk keluar dari akun.
""")

# Catatan tambahan
st.info("Jika mengalami kendala, silakan hubungi admin (arjunyudafirwanda@gmail.com).")

# === Footer ===
st.markdown("---")
st.caption("© 2025 Coffee Shop Analyst Dashboard Created By Arjun Yuda Firwanda")
