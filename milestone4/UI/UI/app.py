import streamlit as st

from components.header import render_header
from components.sidebar import render_sidebar
from app_pages.landing import landing_page
from app_pages.about import about_page
from auth.auth_page import render_auth_page
from app_pages.dashboard import dashboard_page
from app_pages.history import history_page

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ClauseAI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- LOAD CSS ----------------
try:
    with open("styles.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"CSS load error: {e}")

# ---------------- SESSION STATE ----------------
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("user", None)
st.session_state.setdefault("page", "landing")
st.session_state.setdefault("auth_nav_selection", "Login")
st.session_state.setdefault("uploader_key", 0)

# ---------------- HEADER ----------------
render_header()

# ---------------- SIDEBAR ----------------
if st.session_state.authenticated:
    render_sidebar()

# ---------------- ROUTING ----------------
if st.session_state.authenticated:
    if st.session_state.page == "history":
        history_page()
    else:
        # Default authenticated landing
        st.session_state.page = "dashboard"
        dashboard_page()
else:
    if st.session_state.page == "landing":
        landing_page()
    elif st.session_state.page == "auth":
        render_auth_page()
    elif st.session_state.page == "about":
        about_page()
    else:
        landing_page()
