import streamlit as st
from auth.auth import verify_login, register_user
import streamlit as st

st.set_page_config(page_title="Login", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    st.success(f"Selamat datang, {st.session_state.username}!")
    st.switch_page("pages/1_Home.py")

tab_login, tab_register = st.tabs(["🔐 Login", "📝 Register"])

with tab_login:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Masuk"):
        user = verify_login(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user["username"]
            st.session_state.role = user["role"]
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Login gagal! Username/password salah.")

with tab_register:
    st.subheader("Register")
    new_user = st.text_input("Buat Username")
    new_pass = st.text_input("Buat Password", type="password")
    if st.button("Daftar"):
        try:
            register_user(new_user, new_pass)
            st.success("Registrasi berhasil. Silakan login.")
        except:
            st.error("Username sudah digunakan.")
