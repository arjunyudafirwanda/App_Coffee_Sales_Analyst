import streamlit as st
import hashlib


def protect_page(required_role=None):
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("⚠️ Anda harus login terlebih dahulu.")
        st.stop()
    if required_role and st.session_state.get("role") != required_role:
        st.error("❌ Anda tidak punya akses ke halaman ini.")
        st.stop()
        
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

