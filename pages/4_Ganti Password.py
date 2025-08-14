import time
import streamlit as st
import re
from auth.auth import change_password, verify_password, get_user_hashed_password
from utils import protect_page

protect_page()

st.title("🔐 Ganti Password")

# Reset input jika diminta
if st.session_state.get("reset_password_form"):
    for k in ["current_pass", "new_pass", "confirm_pass"]:
        st.session_state.pop(k, None)  # lebih singkat & aman
    st.session_state["reset_password_form"] = False
    st.rerun()

# Informasi profil
role = st.session_state.get("role", "user")
username = st.session_state.get("username", "User")

if "username" not in st.session_state:
    st.error("Anda harus login terlebih dahulu.")
    st.stop()

username = st.session_state.username

st.subheader("Form Ganti Password")

# Token unik untuk reset key widget (default "")
reset_token = st.session_state.get("reset_token", "")

# Input form
current_pass = st.text_input("🔑 Password Saat Ini", type="password", key=f"current_pass_{reset_token}")
new_pass = st.text_input("🆕 Password Baru", type="password", key=f"new_pass_{reset_token}")
confirm_pass = st.text_input("✅ Konfirmasi Password Baru", type="password", key=f"confirm_pass_{reset_token}")

# --- Fungsi cek kekuatan password ---
def check_strength(password):
    checks = {
        "Panjang minimal 8 karakter": len(password) >= 8,
        "Mengandung huruf besar (A-Z)": bool(re.search(r"[A-Z]", password)),
        "Mengandung huruf kecil (a-z)": bool(re.search(r"[a-z]", password)),
        "Mengandung angka (0-9)": bool(re.search(r"\d", password)),
        "Mengandung simbol (!@#$...)": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)),
    }
    return checks

def password_strength_score(checks):
    return sum(checks.values()) / len(checks)

def password_strength_label(score):
    if score < 0.4:
        return "❌ Lemah", "red"
    elif score < 0.8:
        return "⚠️ Sedang", "orange"
    else:
        return "✅ Kuat", "green"

# --- Validasi visual password ---
if new_pass:
    checks = check_strength(new_pass)
    score = password_strength_score(checks)
    label, color = password_strength_label(score)

    st.markdown("**🔍 Kriteria Password:**")
    for desc, passed in checks.items():
        icon = "✅" if passed else "❌"
        color_item = "green" if passed else "red"
        st.markdown(f"<span style='color:{color_item}'>{icon} {desc}</span>", unsafe_allow_html=True)

    st.markdown(f"<br><b>📊 Kekuatan Password:</b> <span style='color:{color}'>{label}</span>", unsafe_allow_html=True)
    st.progress(score)

# --- Proses perubahan password ---
def is_strong_password(pw):
    return all(check_strength(pw).values())

if st.button("🔄 Ganti Password"):
    if not current_pass or not new_pass or not confirm_pass:
        st.warning("⚠️ Semua kolom wajib diisi.")
    elif new_pass != confirm_pass:
        st.error("❌ Konfirmasi password tidak cocok.")
    else:
        hashed = get_user_hashed_password(username)
        if not verify_password(current_pass, hashed):
            st.error("❌ Password saat ini salah.")
        elif current_pass == new_pass:
            st.warning("⚠️ Password baru tidak boleh sama dengan password lama.")
        elif not is_strong_password(new_pass):
            st.warning("⚠️ Password belum memenuhi semua kriteria.")
        else:
            change_password(username, new_pass)            
            st.success("✅ Password berhasil diubah.")
            st.session_state["reset_token"] = str(time.time())
            time.sleep(1.5)
            st.rerun()

# === Profil Sidebar ===
with st.sidebar:
    st.markdown("### 👤 Profil")
    st.markdown(f"**{username.title()}**")
    st.markdown(f"Role: `{role}`")
    
with st.sidebar:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("Dashboard_Analisis_Penjualan_Kopi.py")

# === Footer ===
st.markdown("---")
st.caption("© 2025 Coffee Shop Analyst Dashboard Created By Arjun Yuda Firwanda")
