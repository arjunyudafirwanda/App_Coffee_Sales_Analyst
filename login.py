import streamlit as st
from auth.auth import verify_login
import time

st.set_page_config(page_title="Login", page_icon="🔐")

st.title("🔐 Login Page")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    user = verify_login(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.username = user["username"]
        st.success(f"Selamat datang, {user['username']}!Anda akan diarahkan sebentar lagi...")
        time.sleep(5)
        st.rerun()
        st.switch_page("pages/1_Home.py")
    else:
        st.error("Username atau password salah.")
