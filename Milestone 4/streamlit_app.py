import streamlit as st
import os

from components.header import render_header
from components.sidebar import render_sidebar
from app_pages.landing import landing_page
from app_pages.about import about_page
from auth.auth_page import render_auth_page
from app_pages.dashboard import dashboard_page


st.set_page_config(
    page_title="ClauseAI - AI Contract Analysis",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

try:
    css_file = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_file):
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .main-title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
        }
        .glass-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .info-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .risk-high {
            background-color: #dc2626;
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
        }
        .risk-medium {
            background-color: #f59e0b;
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
        }
        .risk-low {
            background-color: #16a34a;
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
        }
        .risk-critical {
            background-color: #7f1d1d;
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
        }
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 20px;
            border-radius: 20px;
            margin-bottom: 30px;
        }
        </style>
        """, unsafe_allow_html=True)
except Exception as e:
    st.warning(f"CSS loading issue: {e}")

st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("user", None)
st.session_state.setdefault("page", "landing")
st.session_state.setdefault("auth_nav_selection", "Login")
st.session_state.setdefault("analysis_history", [])

render_header()

if st.session_state.authenticated:
    render_sidebar()

if st.session_state.authenticated:
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