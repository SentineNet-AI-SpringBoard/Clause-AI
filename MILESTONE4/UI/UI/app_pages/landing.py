import streamlit as st

def landing_page():
    # Hero Section
    st.markdown(
        """
        <div class="hero">
            <h1 style='text-align: center; font-size: 3rem; margin-bottom: 0.5rem;'>
                ClauseAI
            </h1>
            <p style='text-align: center; font-size: 1.2rem; opacity: 0.8;'>
                AI-powered contract analysis using multi-agent reasoning.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Features Grid
    col1, col2, col3,col4 = st.columns(4)

    with col1:
        st.markdown(
            """
            <div class="glass-card" style='text-align: center;'>
                <h3>⚖️ Legal</h3>
                <p>Analyze indemnity obligations and contractual legal risks.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div class="glass-card" style='text-align: center;'>
                <h3>📋 Compliance</h3>
                <p>Ensure contracts meet regulatory and compliance standards.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    st.markdown("<br><br>", unsafe_allow_html=True)
    with col3:
        st.markdown(
            """
            <div class="glass-card" style='text-align: center;'>
                <h3>💰 Finance</h3>
                <p>Analyze payment terms, penalties, and financial exposure.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            """
            <div class="glass-card" style='text-align: center;'>
                <h3>⚙️ Ops</h3>
                <p>Ensure operational compliance and service level feasibility.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    
    # Call to Action
    st.markdown(
        """
        <div style='text-align: center;'>
            <p>Ready to secure your contracts?</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Centered CTA Button
    _, btn_col, _ = st.columns([1, 1, 1])
    with btn_col:
        if st.button("Get Started Now", use_container_width=True, type="primary"):
            st.session_state.page = "auth"
            st.session_state.auth_nav_selection = "Create Account"
            st.rerun()