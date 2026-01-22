import streamlit as st

def about_page():
    st.markdown("<h1 class='main-title'>About ClauseAI</h1>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="glass-card">
            <h3>🤖 The Future of Contract Intelligence</h3>
            <p style="font-size: 1.1rem; line-height: 1.6;">
                ClauseAI is an advanced multi-agent system designed to autonomously read, analyze,
                and audit legal contracts. By combining specialized AI agents for
                <b>Legal</b>, <b>Compliance</b>, <b>Finance</b>, and <b>Operations</b>,
                we provide a 360° risk assessment in seconds.
            </p>
        </div>
        <br>
        """,
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            "<div class='glass-card'><h5>🚀 Our Mission</h5><span>Empower teams with instant insights.</span></div>",
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            "<div class='glass-card'><h5>🛡️ Security First</h5><span>Encrypted and private processing.</span></div>",
            unsafe_allow_html=True
        )

    st.markdown("---")
    if st.button("Back to Home", type="secondary", use_container_width=True):
        st.session_state.page = "landing"
        st.rerun()
