import streamlit as st
from auth.users import add_user, verify_user

def render_auth_page():
    # If a previous action wants to switch tabs (e.g., after signup), apply it
    # BEFORE the radio widget is created to avoid StreamlitAPIException.
    if st.session_state.get("auth_nav_redirect"):
        st.session_state["auth_nav_selection"] = st.session_state.pop("auth_nav_redirect")

    # st.markdown("<br>", unsafe_/allow_html=True
    
    # Split Layout: Navigation Left, Form Right
    # Adjusted main columns to [1, 2] to make the form container itself slightly narrower
    nav_col, content_col = st.columns([1, 2], gap="small")

    with nav_col:
        st.markdown("### 🔐 Access")
        # Navigation Radio
        selection = st.radio(
            "Menu",
            ["Login", "Create Account", "Forgot Password?"],
            key="auth_nav_selection", # Syncs with session state
            label_visibility="collapsed"
        )
        # st.info("System secure. 256-bit encryption enabled."

    with content_col:
        # The Form Card
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
    
    # 🔥 FIX: Constrain input width
    # Using columns [3, 1] means inputs take 75% of the card width, leaving space on right
    c_input, c_space = st.columns([3, 1])
    
    with c_input:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Login", key="auth_page_login_btn", type="primary"):
            user = verify_user(email, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.page = "dashboard"
                st.rerun()
            st.error("Invalid credentials")

def show_register():
    st.subheader("Create New Account")
    
    # First/Last name already share a row, so they are naturally smaller
    c1, c2 = st.columns(2)
    with c1:
        first = st.text_input("First Name", key="reg_first")
    with c2:
        last = st.text_input("Last Name", key="reg_last")
    
    # Constrain Email & Password width specifically
    c_input, c_space = st.columns([3, 1])
    with c_input:
        email = st.text_input("Work Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Sign Up", key="auth_page_register_btn", type="primary"):
            full_name = " ".join([p for p in [first.strip(), last.strip()] if p])
            ok, msg = add_user(email=email, password=password, name=full_name or first or email)
            if ok:
                st.success(msg)
                # Redirect to Login on next rerun (cannot modify auth_nav_selection after widget instantiation)
                st.session_state["auth_nav_redirect"] = "Login"
                st.rerun()
            else:
                st.error(msg)

def show_forgot():
    st.subheader("Reset Password")
    
    # Constrain input width
    c_input, c_space = st.columns([3, 1])
    with c_input:
        st.text_input("Enter your email")
        st.button("Send Reset Link")