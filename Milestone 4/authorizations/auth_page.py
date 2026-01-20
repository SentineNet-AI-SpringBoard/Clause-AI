import streamlit as st
from auth.users import USERS

def render_auth_page():
    nav_col, content_col = st.columns([1, 2], gap="small")

    with nav_col:
        st.markdown("### 🔐 Access")

        selection = st.radio(
            "Menu",
            ["Login", "Create Account", "Forgot Password?"],
            key="auth_nav_selection", 
            label_visibility="collapsed"
        )

    with content_col:
        with st.container():
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            if selection == "Login":
                show_login()
            elif selection == "Create Account":
                show_register()
            elif selection == "Forgot Password?":
                show_forgot()
            
            st.markdown('</div>', unsafe_allow_html=True)

def show_login():
    st.subheader("Welcome Back")
    
    c_input, c_space = st.columns([3, 1])
    
    with c_input:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Login", key="auth_page_login_btn", type="primary"):
            if email in USERS and USERS[email]["password"] == password:
                st.session_state.authenticated = True
                st.session_state.user = USERS[email]
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials")

def show_register():
    st.subheader("Create New Account")
    c1, c2 = st.columns(2)
    with c1: st.text_input("First Name")
    with c2: st.text_input("Last Name")
    
    c_input, c_space = st.columns([3, 1])
    with c_input:
        st.text_input("Work Email")
        st.text_input("Password", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Sign Up", key="auth_page_register_btn", type="primary"):
            st.success("Account created! Please switch to Login tab.")

def show_forgot():
    st.subheader("Reset Password")
    
    c_input, c_space = st.columns([3, 1])
    with c_input:
        st.text_input("Enter your email")
        st.button("Send Reset Link")