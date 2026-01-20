import streamlit as st

def render_sidebar():
    
    with st.sidebar:
        st.markdown("### 🗂️ Workspace")
        
        if st.button("📊 New Analysis", key="sidebar_new_analysis", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

        st.divider()

        st.markdown("#### 🕒 Recent Contracts")
        
        history_items = [
            "NDA_Google_v2.pdf",
            "Service_Agreement_Q1.docx",
            "Emp_Contract_J_Doe.pdf"
        ]

        for i, item in enumerate(history_items):
            if st.button(f"📄 {item}", key=f"history_btn_{i}", help="Load this analysis"):
                st.toast(f"Loading analysis for {item}...")

        st.divider()

        st.markdown("#### ⚙️ Settings")
        st.checkbox("Dark Mode Support", value=True, key="setting_dark_mode")
        st.checkbox("Auto-Escalate Risks", value=False, key="setting_auto_escalate")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🚪 Logout", key="sidebar_logout_btn", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.page = "landing"
            st.rerun()