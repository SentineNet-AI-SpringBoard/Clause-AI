import streamlit as st

def navbar():
    col1, col2 = st.columns([6, 1])

    with col1:
        st.markdown("### 🧠 ClauseAI")

    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()
