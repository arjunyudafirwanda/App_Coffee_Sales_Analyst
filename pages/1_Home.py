import streamlit as st
from utils import protect_page

# === Proteksi Login ===
protect_page()

# === Judul dan Deskripsi Halaman ===
st.title("🏠 Beranda Dashboard")
st.markdown("""
Selamat datang di **Dashboard Penjualan Kopi**.  
Lihat performa bisnis Anda secara ringkas dan interaktif:

- 🔍 Analisis total penjualan dan jumlah transaksi  
- 📈 Grafik interaktif produk kopi terlaris  
- 💡 Insight untuk keputusan bisnis lebih baik  
""")

# === Info User dari Session ===
role = st.session_state.get("role", "user")
username = st.session_state.get("username", "User")

# === Sidebar Profil ===
with st.sidebar:
    st.markdown("### 👤 Profil")
    st.markdown(f"**{username.title()}**")
    st.markdown(f"Role: `{role}`")

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("Dashboard_Analisis_Penjualan_Kopi.py")

# === Footer ===
st.markdown("---")
st.caption("© 2025 Coffee Shop Analyst Dashboard Created By Arjun Yuda Firwanda")
