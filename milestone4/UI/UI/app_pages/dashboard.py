import streamlit as st
import time
import json
from services.analysis import ContractAnalyzer
from services.history import save_run

def dashboard_page():
    # Surface any history-load error from sidebar/history page.
    if st.session_state.get("history_load_error"):
        st.error(st.session_state.pop("history_load_error"))

    # --- HEADER ---
    st.markdown("<h1 class='main-title' style='margin-bottom:5px;'>Contract Intelligence Command Center</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#334155; font-weight:500;'>Multi-agent swarm ready for analysis.</p>", unsafe_allow_html=True)

    # --- HUD ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="info-box"><h5>⚖️ Legal</h5><span>Risk Guard Ready</span></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="info-box"><h5>📋 Compliance</h5><span>GDPR Check Ready</span></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="info-box"><h5>💰 Finance</h5><span>Term Analysis Ready</span></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="info-box"><h5>⚙️ Ops</h5><span>SLA Verifier Ready</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ACTION DECK ---       
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # CENTERING LAYOUT using 3 columns
    col_l, col_center, col_r = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("<h5 style='text-align: center; color: #0f172a;'>Upload Documents</h5>", unsafe_allow_html=True)
        
        # 1. DRAG & DROP ZONE
        uploader_key = int(st.session_state.get("uploader_key") or 0)
        files = st.file_uploader(
            "Contract files",
            type=["txt", "pdf", "docx"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key=f"contract_uploader_{uploader_key}",
        )
        
        # 🔥 SHOW UPLOADED FILES EXPLICITLY BELOW BOX
        if files:
            st.markdown("<br>", unsafe_allow_html=True)
            for f in files:
                st.markdown(
                    f"""
                    <div class='uploaded-file'>
                        <span class='uploaded-file-icon'>📄</span>
                        <span class='uploaded-file-name'>{f.name}</span>
                        <span class='uploaded-file-size'>{f.size / 1024:.1f} KB</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

        # If user loaded a previous run from History but hasn't uploaded files now,
        # still show the saved results so "click last report" feels responsive.
        if not files:
            answer_results = st.session_state.get("answer_results")
            if answer_results:
                st.markdown("---")
                st.markdown("### Saved Answer")
                for idx, r in enumerate(answer_results):
                    fname = (r or {}).get("filename", f"file_{idx}") if isinstance(r, dict) else f"file_{idx}"
                    if isinstance(r, dict) and r.get("error"):
                        st.error(f"{fname}: {r.get('error')}")
                        continue
                    st.markdown(f"({fname})")
                    st.markdown((r or {}).get("report", "") if isinstance(r, dict) else "")

        # --- QUESTION + ANSWER MODE (Ask) ---
        ask_btn = False
        q = ""
        if files:
            st.markdown("---")
            st.markdown("##### Ask a question about these documents")
            q = st.text_area(
                "Question",
                placeholder="Example: Summarize payment terms and late fees",
                height=80,
                key="query_box_input",
                label_visibility="collapsed",
            )
            ask_btn = st.button("Ask", type="secondary", key="ask_btn")

            # Render answer FIRST (above all analysis controls)
            answer_results = st.session_state.get("answer_results")
            if answer_results:
                st.markdown("---")
                st.markdown("### Answer to your question")
                for idx, r in enumerate(answer_results):
                    fname = r.get("filename", f"file_{idx}")
                    if isinstance(r, dict) and r.get("error"):
                        st.error(f"{fname}: {r.get('error')}")
                        continue
                    # Backend returns strict fact_summary markdown in `report`.
                    st.markdown(f"({fname})")
                    st.markdown(r.get("report", ""))

        st.markdown("<br>", unsafe_allow_html=True)

        # --- ANALYSIS CONTROLS + REPORT MODE (Launch Analysis) ---
        tone = st.selectbox("Analysis Tone", ["Professional", "Executive", "Technical", "Simple"])
        no_evidence_threshold = st.slider("No-evidence threshold", 0.05, 0.50, 0.15, 0.05)

        full_review = st.checkbox(
            "Full review (run all agents)",
            value=False,
            help="Runs legal, compliance, finance, and operations even if your question is narrow. Use for whole-contract reviews.",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        analyze_btn = st.button("Launch Analysis", key="dash_analyze", type="primary", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    analyzer = ContractAnalyzer()
    q = (st.session_state.get("query_box_input") or "").strip()

    user = st.session_state.get("user") or {}
    user_email = (user.get("email") or "").strip().lower() if isinstance(user, dict) else ""
    token = (user.get("token") or "").strip() if isinstance(user, dict) else ""

    # Ask => answer mode only
    if files and ask_btn:
        if not q:
            st.warning("Please enter a question, then click Ask.")
            return

        progress = st.progress(0)
        status = st.empty()
        answers = []
        for i, f in enumerate(files):
            status.markdown(f"**Answering:** `{f.name}`...")
            file_bytes = f.getvalue()
            res = analyzer.analyze_file(
                file_bytes=file_bytes,
                filename=f.name,
                question=q,
                tone=tone,
                no_evidence_threshold=float(no_evidence_threshold),
                intent_override="fact_summary",
            )
            res["filename"] = f.name
            answers.append(res)
            progress.progress((i + 1) / len(files))
        progress.empty()
        status.empty()
        st.session_state["answer_results"] = answers

        # Persist run for history (only when logged in).
        if user_email and token:
            try:
                save_run(
                    token=token,
                    mode="ask",
                    question=q,
                    tone=tone,
                    run_all_agents=False,
                    no_evidence_threshold=float(no_evidence_threshold),
                    filenames=[f.get("filename") for f in answers if isinstance(f, dict) and f.get("filename")],
                    results=answers,
                )
            except Exception:
                pass

        # Clear any previous reports so we never show report by default.
        st.session_state.pop("report_results", None)

        # Re-render to place the answer section above controls.
        st.rerun()

    # Launch Analysis => report mode
    if files and analyze_btn:
        # If no question provided, use a default analysis question.
        if not q:
            q = "Summarize key risks, payment terms, termination, liability, and compliance obligations."

        st.markdown("### Final Executive Report")
        progress = st.progress(0)
        status = st.empty()
        reports = []
        for i, f in enumerate(files):
            status.markdown(f"**Analyzing:** `{f.name}`...")
            time.sleep(0.2)
            file_bytes = f.getvalue()
            res = analyzer.analyze_file(
                file_bytes=file_bytes,
                filename=f.name,
                question=q,
                tone=tone,
                no_evidence_threshold=float(no_evidence_threshold),
                intent_override="risk_analysis",
                run_all_agents=bool(full_review),
            )
            res["filename"] = f.name
            reports.append(res)
            progress.progress((i + 1) / len(files))
        progress.empty()
        status.empty()
        st.session_state["report_results"] = reports

        # Persist run for history (only when logged in).
        if user_email and token:
            try:
                save_run(
                    token=token,
                    mode="analysis",
                    question=q,
                    tone=tone,
                    run_all_agents=bool(full_review),
                    no_evidence_threshold=float(no_evidence_threshold),
                    filenames=[f.get("filename") for f in reports if isinstance(f, dict) and f.get("filename")],
                    results=reports,
                )
            except Exception:
                pass

    # Render report results ONLY if Launch Analysis has been clicked.
    report_results = st.session_state.get("report_results")
    if report_results:
        for i, r in enumerate(report_results):
            if isinstance(r, dict) and r.get("error"):
                with st.expander(f"⚠️ {r.get('filename', 'file')} — ERROR"):
                    st.error(r.get("error"))
                    if r.get("detail"):
                        st.json(r.get("detail"))
                continue

            if r.get("no_evidence") is True:
                score = r.get("evidence_score")
                st.info(
                    f"No evidence found for this question in the uploaded document. "
                    f"Try lowering the threshold (current={no_evidence_threshold}) or rephrasing the question. "
                    f"(evidence_score={score})"
                )

            risk = (r.get('analysis') or {}).get('overall_risk') or "unknown"
            icon = "🔴" if risk == "high" else "🟡" if risk == "medium" else "🟢"
            with st.expander(f"{icon} {r['filename']} — {risk.upper()}"):
                st.markdown(f'<div class="risk-{risk}" style="text-align:center;">{risk.upper()} RISK</div>', unsafe_allow_html=True)
                t1, t2 = st.tabs(["Report", "Data"])
                with t1:
                    # Transparency: show which agents were executed.
                    selected = ((r.get("agent_analysis") or {}).get("selected_agents") or [])
                    if selected:
                        st.caption(f"Agents run: {', '.join(selected)}")
                    # Full executive/multi-agent report
                    st.code(r.get("report", ""), language="markdown")
                with t2:
                    st.json(r)