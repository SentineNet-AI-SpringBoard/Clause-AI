from __future__ import annotations

import time
import base64
from datetime import datetime, timezone
from typing import Any, Dict, List

import streamlit as st
from services.analysis import ContractAnalyzer
from services.history import save_run

from utils.report_pdf import make_pdf_filename, run_to_pdf_bytes
from components.final_report import JsonEvidencePanel, ReportSummary
from components.pdf_preview import PDFPreviewWithHighlights, ConfirmationPanel
from components.qa_report import QuestionAnswerReport, QuestionAnswerWithPDF

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
    # NOTE: Avoid trying to wrap Streamlit widgets with raw HTML <div> wrappers.
    # Streamlit renders widgets in separate containers, which can leave a stray empty
    # styled div on the page and make the uploader look "misplaced".

    # STEP 1: Upload Documents (centered layout)
    st.markdown("<h5 style='text-align: center; color: #0f172a;'>📤 Step 1: Upload Documents</h5>", unsafe_allow_html=True)
    
    # 1. DRAG & DROP ZONE
    uploader_key = int(st.session_state.get("uploader_key") or 0)
    files = st.file_uploader(
        "Contract files",
        type=["pdf"],  # Restrict to PDF for preview feature
        accept_multiple_files=False,  # Single file for better UX
        label_visibility="collapsed",
        key=f"contract_uploader_{uploader_key}",
        help="Upload a PDF contract to preview and analyze"
    )
    
    # 🔥 SHOW UPLOADED FILE EXPLICITLY BELOW BOX
    if files:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class='uploaded-file' style='background: #ecfdf5; border: 1px solid #10b981; border-radius: 8px; padding: 12px; margin: 0 auto; max-width: 600px; text-align: center;'>
                <span class='uploaded-file-icon'>✓</span>
                <span class='uploaded-file-name' style='font-weight: 600;'>{files.name}</span>
                <span class='uploaded-file-size' style='margin-left: 8px; color: #64748b;'>{files.size / 1024:.1f} KB</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Check if we already have results - skip preview if so
    has_results = st.session_state.get("analysis_result") is not None
    
    # STEP 2: Preview with Pre-Highlighting (skip if results already exist)
    if files and not has_results:
        # Check if already confirmed
        if not st.session_state.get("preview_confirmed", False):
            st.markdown("---")
            st.markdown("<h5 style='text-align: center; color: #0f172a;'>👁️ Step 2: Preview Document</h5>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 20px;'>Review your document to confirm it's correct before analysis.</p>", unsafe_allow_html=True)
            
            # Show PDF preview with auto-highlights
            file_bytes = files.getvalue()
            PDFPreviewWithHighlights(file_bytes, files.name)
            
            # Confirmation button
            if ConfirmationPanel():
                st.session_state["preview_confirmed"] = True
                st.rerun()
            else:
                st.stop()  # Wait for user confirmation
        
        # STEP 3: Analysis Configuration (only show after confirmation)
        if st.session_state.get("preview_confirmed", False):
            st.markdown("---")
            st.markdown("<h5 style='text-align: center; color: #0f172a;'>⚙️ Step 3: Configure Analysis</h5>", unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                q = st.text_area(
                    "Analysis Question (optional)",
                    placeholder="Example: What are the termination and payment terms?",
                    height=100,
                    key="query_box_input",
                    help="Leave empty for comprehensive contract analysis"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            with col_btn2:
                analyze_btn = st.button(
                    "🚀 Start Analysis", 
                    type="primary", 
                    use_container_width=True,
                    key="start_analysis_btn"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        # Set defaults for when not in configuration mode
        analyze_btn = False

    
    analyzer = ContractAnalyzer()
    q = (st.session_state.get("query_box_input") or "").strip()
    tone = "Executive"  # Default tone for initial analysis
    full_review = True  # Always run full review for initial analysis

    user = st.session_state.get("user") or {}
    user_email = (user.get("email") or "").strip().lower() if isinstance(user, dict) else ""
    token = (user.get("token") or "").strip() if isinstance(user, dict) else ""

    # Initialize QA history
    if "qa_history" not in st.session_state:
        st.session_state["qa_history"] = []

    # STEP 4: Run Analysis
    if files and analyze_btn and st.session_state.get("preview_confirmed", False):
        st.markdown("---")
        st.markdown("<h5 style='text-align: center; color: #0f172a;'>⚡ Step 4: Analyzing...</h5>", unsafe_allow_html=True)
        
        intent_override = None
        # If no question provided, use comprehensive analysis
        if not q:
            q = "Provide comprehensive contract analysis covering risks, payment terms, termination, liability, and compliance."
            intent_override = "risk_analysis"
        
        progress = st.progress(0)
        status = st.empty()
        
        status.markdown(f"**📄 Analyzing:** `{files.name}`...")
        file_bytes = files.getvalue()
        
        res = analyzer.analyze_file(
            file_bytes=file_bytes,
            filename=files.name,
            question=q,
            tone=tone,
            no_evidence_threshold=0.15,
            intent_override=intent_override,
            run_all_agents=bool(full_review),
        )
        res["filename"] = files.name
        res["_file_b64"] = base64.b64encode(file_bytes).decode("utf-8")
        res["_file_mime"] = "application/pdf"
        
        progress.progress(1.0)
        progress.empty()
        status.empty()
        
        # Append to history
        st.session_state["qa_history"].append(res)
        st.session_state["analysis_result"] = res
        st.session_state["analysis_pdf_bytes"] = file_bytes
        st.session_state["last_analysis_q"] = q  # Store for report generation
        st.session_state["last_analysis_time"] = datetime.now(timezone.utc).isoformat()

        # Persist run for history (only when logged in)
        if user_email and token:
            try:
                cleaned_res = {k: v for k, v in res.items() if k not in {"_file_b64", "_file_mime"}}
                save_run(
                    token=token,
                    mode="analysis",
                    question=q,
                    tone=tone,
                    run_all_agents=bool(full_review),
                    no_evidence_threshold=0.15,
                    filenames=[files.name],
                    results=[cleaned_res],
                )
            except Exception:
                pass
        
        st.success("✅ Analysis complete!")
        st.rerun()
    
    # STEP 5: Display Results (Q&A Format)
    qa_history = st.session_state.get("qa_history", [])
    analysis_pdf_bytes = st.session_state.get("analysis_pdf_bytes")
    analysis_result = st.session_state.get("analysis_result")
    
    if qa_history:
        st.markdown("---")
        
        # Add a "New Analysis" button at the top
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Start New Analysis", use_container_width=True, key="new_analysis_btn"):
                # Clear all analysis-related session state
                st.session_state.pop("analysis_result", None)
                st.session_state.pop("qa_history", None)
                st.session_state.pop("analysis_pdf_bytes", None)
                st.session_state.pop("preview_confirmed", None)
                st.session_state["uploader_key"] = int(st.session_state.get("uploader_key", 0)) + 1
                st.rerun()
        
        st.markdown("<h5 style='text-align: center; color: #0f172a;'>📊 Analysis Results</h5>", unsafe_allow_html=True)
        
        # Display Q&A with PDF (split view)
        QuestionAnswerWithPDF(qa_history, analysis_pdf_bytes)

        # Allow follow-up questions
        st.markdown("---")
        st.markdown("<h6 style='text-align: center; color: #0f172a;'>💬 Ask a follow-up question</h6>", unsafe_allow_html=True)
        
        col_q1, col_q2, col_q3 = st.columns([1, 2, 1])
        with col_q2:
            follow_up_q = st.text_input(
                "Question",
                placeholder="e.g. What is the governing law?",
                label_visibility="collapsed",
                key="follow_up_input"
            )
            
            if st.button("Ask Question", type="primary", use_container_width=True, key="ask_follow_up_btn"):
                if follow_up_q:
                    # Use stored bytes if available (more reliable than re-reading files uploader)
                    current_bytes = analysis_pdf_bytes or (files.getvalue() if files else None)
                    current_name = (analysis_result or {}).get("filename") or (files.name if files else "document.pdf")
                    
                    if current_bytes:
                        progress_sub = st.progress(0)
                        with st.spinner("Analyzing..."):
                            res_sub = analyzer.analyze_file(
                                file_bytes=current_bytes,
                                filename=current_name,
                                question=follow_up_q,
                                tone=tone,
                                no_evidence_threshold=0.15,
                                intent_override="qa", 
                                run_all_agents=False,
                            )
                            res_sub["filename"] = current_name
                            
                            st.session_state["qa_history"].append(res_sub)
                        progress_sub.empty()
                        st.rerun()

        
        # STEP 6: Generate Full Executive Report
        st.markdown("---")
        st.markdown("<h5 style='text-align: center; color: #0f172a;'>📑 Generate Comprehensive Report</h5>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #64748b; margin-bottom: 20px;'>Create a detailed executive report with all analysis sections</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            report_tone = st.selectbox(
                "Report Tone", 
                ["Executive", "Professional", "Technical", "Simple"], 
                key="report_tone_select",
                help="Choose the tone for the final report"
            )
            full_review_report = st.checkbox(
                "Run comprehensive review (all agents)",
                value=True,
                help="Check to run all agents. Uncheck to automatically select relevant agents based on your analysis question.",
                key="full_review_report_check"
            )
            
            if not full_review_report:
                st.info("ℹ️ Agents will be automatically selected based on your analysis question.")

            no_evidence_threshold = st.slider(
                "No-evidence threshold", 
                0.05, 0.50, 0.15, 0.05,
                key="no_evidence_slider",
                help="Lower threshold = more findings included"
            )
            
            generate_report_btn = st.button(
                "📊 Generate Final Report", 
                type="primary", 
                use_container_width=True,
                key="generate_final_report_btn"
            )
        
        # Generate comprehensive report
        if generate_report_btn:
            st.markdown("---")
            st.markdown("<h5 style='text-align: center; color: #0f172a;'>⚡ Generating Report...</h5>", unsafe_allow_html=True)
            
            progress = st.progress(0)
            status = st.empty()
            
            status.markdown(f"**📄 Running comprehensive analysis...**")
            
            # Re-analyze with all agents for comprehensive report
            full_review_setting = st.session_state.get("full_review_report_check", True)
            
            # Construct appropriate question based on mode
            if full_review_setting:
                report_question = "Provide comprehensive contract analysis covering all risks, payment terms, termination, liability, compliance, and operational requirements."
            else:
                # Auto-detect intent from previous analysis question
                last_q = st.session_state.get("last_analysis_q")
                
                # Check if last_q is the generic default string - if so, we can't be specific
                is_generic = last_q and "Provide comprehensive contract analysis" in last_q
                
                if last_q and not is_generic:
                    report_question = last_q
                else:
                    # Fallback
                    report_question = "Provide contract analysis."

            status.markdown(f"**📄 Running {'comprehensive' if full_review_setting else 'focused'} analysis...**")

            res = analyzer.analyze_file(
                file_bytes=analysis_pdf_bytes,
                filename=analysis_result.get("filename", "document.pdf"),
                question=report_question,
                tone=report_tone,
                no_evidence_threshold=float(no_evidence_threshold),
                intent_override="risk_analysis",
                run_all_agents=bool(full_review_setting),
            )
            
            progress.progress(1.0)
            progress.empty()
            status.empty()
            
            # Store full report
            st.session_state["full_report_result"] = res
            st.session_state["full_report_time"] = datetime.now(timezone.utc).isoformat()
            
            st.success("✅ Report generated!")
            st.rerun()
        
        # Display Full Report if generated
        full_report = st.session_state.get("full_report_result")
        if full_report:
            st.markdown("---")
            st.markdown("<h5 style='text-align: center; color: #0f172a;'>📋 Final Executive Report</h5>", unsafe_allow_html=True)
            
            # Download button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                run_data = {
                    "mode": "analysis",
                    "created_at": st.session_state.get("full_report_time", ""),
                    "question": "Comprehensive Analysis",
                    "tone": report_tone,
                    "results": [full_report],
                }
                st.download_button(
                    "📥 Download PDF Report",
                    data=run_to_pdf_bytes(run_data),
                    file_name=make_pdf_filename(mode="analysis", run_id="full-report"),
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_full_report_btn"
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Show report with tabs: Human-readable + PDF highlights
            risk = (full_report.get('analysis') or {}).get('overall_risk') or "unknown"
            risk_color = "#dc2626" if risk == "high" else "#f59e0b" if risk == "medium" else "#16a34a"
            risk_bg = "#fee2e2" if risk == "high" else "#fef3c7" if risk == "medium" else "#dcfce7"
            
            st.markdown(f"""
            <div style='background: {risk_bg}; border-left: 4px solid {risk_color}; padding: 16px; margin-bottom: 20px; border-radius: 6px;'>
                <h3 style='margin: 0; color: {risk_color};'>⚠️ Overall Risk Level: {risk.upper()}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            t1, t2 = st.tabs(["📄 Executive Summary", "🔍 Evidence & Source"])
            
            with t1:
                # Show which agents were executed
                selected = ((full_report.get("agent_analysis") or {}).get("selected_agents") or [])
                if selected:
                    st.caption(f"Agents run: {', '.join(selected)}")
                ReportSummary(full_report)
            
            with t2:
                # Show PDF with highlights of evidence used
                file_b64 = full_report.get("_file_b64")
                if not file_b64 and analysis_pdf_bytes:
                    file_b64 = base64.b64encode(analysis_pdf_bytes).decode("utf-8")
                    full_report["_file_b64"] = file_b64
                
                file_bytes = base64.b64decode(file_b64) if isinstance(file_b64, str) and file_b64 else analysis_pdf_bytes
                JsonEvidencePanel(full_report, file_bytes)