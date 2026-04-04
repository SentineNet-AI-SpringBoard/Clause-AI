import streamlit as st
import os

def render_header():
    col1, col2 = st.columns([7, 3])

    # 🟢 LEFT: LOGO (DISPLAY ONLY)
    with col1:
        logo_path = os.path.join("assets", "logo.png")  # make sure folder is 'assets'

        if os.path.exists(logo_path):
            st.image(logo_path, width=75)
        else:
            # Fallback creative text logo (no button, no navigation)
            st.markdown(
                """
                <div class="logo-container">
                    <p>ClauseAI</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    # 🔵 RIGHT: AUTH / PROFILE CONTROLS
    with col2:
        if st.session_state.get("authenticated"):
            user = st.session_state.get("user", {})
            with st.expander(f"👤 {user.get('name', 'User')}"):
                st.caption(f"Role: {user.get('role', 'Member')}")
                st.divider()

                if st.button("Logout", key="header_logout_btn", use_container_width=True):
                    st.session_state.authenticated = False
                    st.session_state.user = None
                    st.session_state.page = "landing"
                    st.rerun()
        else:
            if st.session_state.get("page") != "landing":
                b1, b2, b3 = st.columns(3)

                with b1:
                    if st.button("About", key="header_about_btn", use_container_width=True):
                        st.session_state.page = "about"
                        st.rerun()

                with b2:
                    if st.button("Login", key="header_login_btn", use_container_width=True):
                        st.session_state.page = "auth"
                        st.session_state.auth_nav_selection = "Login"
                        st.rerun()

                with b3:
                    if st.button("Register", key="header_register_btn", use_container_width=True):
                        st.session_state.page = "auth"
                        st.session_state.auth_nav_selection = "Create Account"
                        st.rerun()
