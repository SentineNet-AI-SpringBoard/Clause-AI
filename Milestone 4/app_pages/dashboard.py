import streamlit as st
import time
import json
import requests
from datetime import datetime

API_BASE_URL = "http://127.0.0.1:8000"

def check_api_status():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        return response.status_code == 200, response.json()
    except:
        return False, None

def analyze_contract_with_api(contract_text: str, tone: str = "professional"):

    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze",
            json={"contract_text": contract_text, "tone": tone.lower()},
            timeout=18000  
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"API Error: {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "Analysis timed out. Please try with a shorter contract."
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to AI backend. Please ensure the API server is running."
    except Exception as e:
        return False, f"Error: {str(e)}"

def upload_file_to_api(file):
    try:
        files = {"file": (file.name, file, file.type)}
        response = requests.post(
            f"{API_BASE_URL}/analyze/upload",
            files=files,
            timeout=180
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Upload Error: {response.status_code}"
    except Exception as e:
        return False, f"Upload failed: {str(e)}"

def render_risk_indicator(risk_level: str):
    risk_level = risk_level.lower()
    if risk_level == "critical":
        return "🔴", "CRITICAL", "#dc2626"
    elif risk_level == "high":
        return "🟠", "HIGH", "#ea580c"
    elif risk_level == "medium":
        return "🟡", "MEDIUM", "#f59e0b"
    else:
        return "🟢", "LOW", "#16a34a"

def dashboard_page():

    st.markdown("<h1 class='main-title' style='margin-bottom:5px;'>Contract Intelligence Command Center</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#334155; font-weight:500;'>Multi-agent AI swarm ready for analysis.</p>", unsafe_allow_html=True)

    api_available, api_health = check_api_status()
    
    if api_available:
        st.success
    else:
        st.error("AI Backend Offline - Please start the backend server: `python app.py`")
        st.info("Tip: The backend must be running on http://localhost:8000")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="info-box"><h5>⚖️ Legal</h5><span>Risk Guard Ready</span></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="info-box"><h5>📋 Compliance</h5><span>GDPR Check Ready</span></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="info-box"><h5>💰 Finance</h5><span>Term Analysis Ready</span></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="info-box"><h5>⚙️ Ops</h5><span>SLA Verifier Ready</span></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
   
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("<h5 style='text-align: center; color: #0f172a;'>Upload Documents</h5>", unsafe_allow_html=True)
        
        files = st.file_uploader("", type=["txt", "pdf", "docx"], accept_multiple_files=True, key="contract_uploader")
        
        if files:
            st.markdown("<br>", unsafe_allow_html=True)
            for f in files:
                st.markdown(
                    f"""
                    <div style='background-color: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px; margin-bottom: 5px; color: #020617; font-weight: 600; display: flex; align-items: center;'>
                        <span style='margin-right: 10px; font-size: 1.2rem;'>📄</span> 
                        {f.name} 
                        <span style='margin-left: auto; color: #64748b; font-size: 0.8rem;'>{f.size / 1024:.1f} KB</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

        if files:
            st.markdown("---")
            st.markdown("##### 🔍 Ask a question about these documents")
            query = st.text_area("", placeholder="Example: What are the termination conditions?", height=80, key="query_box_input", label_visibility="collapsed")
            if st.button("Ask", type="secondary", key="ask_btn"):
                if query.strip():
                    st.info(f"💬 Query: {query}")
                    st.warning("⚠️ Query feature coming soon - currently processing full analysis")

        st.markdown("<br>", unsafe_allow_html=True)
        
        tone = st.selectbox("Analysis Tone", ["Professional", "Executive", "Technical", "Simple"], key="tone_selector")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        analyze_btn = st.button("Launch AI Analysis", key="dash_analyze", type="primary", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if files and analyze_btn:
        st.markdown("### 🧠 AI Analysis Stream")
        
        progress = st.progress(0)
        status = st.empty()
        results = []
        
        for i, f in enumerate(files):
            status.markdown(f"**🔄 Processing:** `{f.name}` with Multi-Agent AI System...")
            
            try:
                content = f.getvalue()
                try:
                    contract_text = content.decode("utf-8")
                except:
                    contract_text = content.decode("latin-1")
                
                if len(contract_text.strip()) < 100:
                    st.error(f"❌ File `{f.name}` is too short (minimum 100 characters required)")
                    continue
                
                success, result = analyze_contract_with_api(contract_text, tone)
                
                if success:
                    result["filename"] = f.name
                    results.append(result)
                    status.success(f"✅ Completed: `{f.name}`")
                else:
                    st.error(f"❌ Analysis failed for `{f.name}`: {result}")
                    
            except Exception as e:
                st.error(f"❌ Error processing `{f.name}`: {str(e)}")
            
            progress.progress((i + 1) / len(files))
            time.sleep(0.5)
        
        progress.empty()
        status.success("✅ All analyses complete!")
        
        if results:
            st.markdown("---")
            st.markdown("### 📊 Analysis Results")
            
            for i, result in enumerate(results):

                overall_risk = result.get('overall_assessment', {}).get('overall_risk', 'unknown')
                icon, risk_text, risk_color = render_risk_indicator(overall_risk)
                
                with st.expander(f"{icon} {result['filename']} — {risk_text} RISK", expanded=True):

                    st.markdown(
                        f'<div class="risk-{overall_risk.lower()}" style="text-align:center; padding: 15px; border-radius: 10px; margin-bottom: 20px;">'
                        f'<h3 style="margin:0; color: white;">{icon} {risk_text} RISK</h3>'
                        f'</div>', 
                        unsafe_allow_html=True
                    )
                    
                    tab_summary, tab_agents, tab_clauses, tab_raw = st.tabs([
                        "📋 Executive Summary", 
                        "🤖 Agent Reports", 
                        "⚠️ High-Risk Clauses",
                        "📊 Raw Data"
                    ])
                    
                    with tab_summary:
                        st.markdown("#### Overall Assessment")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(
                                "Overall Risk", 
                                overall_risk.upper(),
                                help="Aggregate risk across all domains"
                            )
                        with col2:
                            overall_conf = result.get('overall_assessment', {}).get('overall_confidence', 0)
                            st.metric(
                                "Confidence", 
                                f"{overall_conf:.0%}",
                                help="AI confidence in risk assessment"
                            )
                        with col3:
                            proc_time = result.get('processing_time_seconds', 0)
                            st.metric(
                                "Processing Time", 
                                f"{proc_time:.1f}s",
                                help="Total analysis duration"
                            )
                        
                        st.markdown("---")
                        
                        risk_dist = result.get('overall_assessment', {}).get('risk_distribution', {})
                        st.markdown("#### Risk Distribution Across Domains")
                        
                        dist_col1, dist_col2, dist_col3, dist_col4 = st.columns(4)
                        with dist_col1:
                            st.metric("Critical", risk_dist.get('critical', 0))
                        with dist_col2:
                            st.metric("High", risk_dist.get('high', 0))
                        with dist_col3:
                            st.metric("Medium", risk_dist.get('medium', 0))
                        with dist_col4:
                            st.metric("Low", risk_dist.get('low', 0))
                    
                    with tab_agents:
                        st.markdown("#### Individual Agent Assessments")
                        
                        agents = result.get('agent_assessments', {})
                        
                        for agent_name in ['legal', 'compliance', 'finance', 'operations']:
                            agent_data = agents.get(agent_name, {})
                            
                            if agent_data:
                                agent_risk = agent_data.get('risk_level', 'unknown')
                                a_icon, a_text, a_color = render_risk_indicator(agent_risk)
                                
                                with st.container():
                                    st.markdown(f"**{a_icon} {agent_name.upper()} Agent**")
                                    
                                    a_col1, a_col2, a_col3 = st.columns(3)
                                    with a_col1:
                                        st.metric("Risk", agent_risk.upper())
                                    with a_col2:
                                        st.metric("Confidence", f"{agent_data.get('confidence', 0):.0%}")
                                    with a_col3:
                                        st.metric("Clauses", agent_data.get('num_clauses', 0))
                                    
                                    analysis_text = agent_data.get('enhanced_analysis', '')
                                    if analysis_text:
                                        with st.expander("📝 AI Analysis", expanded=False):
                                            st.write(analysis_text)
                                    
                                    st.markdown("---")
                    
                    with tab_clauses:
                        st.markdown("#### High-Risk Clauses Identified")
                        
                        high_risk_clauses = result.get('high_risk_clauses', [])
                        
                        if high_risk_clauses:
                            for idx, clause in enumerate(high_risk_clauses, 1):
                                with st.container():
                                    c_risk = clause.get('risk_level', 'unknown')
                                    c_icon, c_text, c_color = render_risk_indicator(c_risk)
                                    
                                    st.markdown(f"**{c_icon} Clause #{idx} - {c_text} Risk**")
                                    st.text_area(
                                        "Clause Text:", 
                                        clause.get('clause', 'N/A'),
                                        height=100,
                                        key=f"clause_{i}_{idx}",
                                        disabled=True
                                    )
                                    st.markdown("---")
                        else:
                            st.success("✅ No high-risk clauses identified")
                    
                    with tab_raw:
                        st.markdown("#### Complete Analysis Data (JSON)")
                        st.json(result)
                        
                        json_str = json.dumps(result, indent=2)
                        st.download_button(
                            label="💾 Download JSON",
                            data=json_str,
                            file_name=f"analysis_{result.get('contract_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            key=f"download_{i}"
                        )
        else:
            st.warning("⚠️ No successful analyses to display")
    
    elif 'analysis_history' in st.session_state and st.session_state.analysis_history:
        st.markdown("---")
        st.markdown("### 📁 Recent Analysis History")
        
        for idx, hist_result in enumerate(st.session_state.analysis_history[-3:]):  # Show last 3
            filename = hist_result.get('filename', 'Unknown')
            risk = hist_result.get('overall_assessment', {}).get('overall_risk', 'unknown')
            icon, risk_text, _ = render_risk_indicator(risk)
            
            if st.button(f"{icon} {filename} - {risk_text}", key=f"hist_{idx}"):
                st.session_state.selected_history = hist_result
                st.rerun()