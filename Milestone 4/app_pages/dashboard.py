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

def truncate_filename(filename: str, max_length: int = 40) -> str:
    """Truncate filename if too long, preserving extension"""
    if len(filename) <= max_length:
        return filename
    
    parts = filename.rsplit('.', 1)
    if len(parts) == 2:
        name, ext = parts
        available = max_length - len(ext) - 4  
        if available > 0:
            return f"{name[:available]}...{ext}"
    
    return filename[:max_length-3] + "..."

def save_report_to_db(user_id: int, filename: str, analysis_result: dict):
    try:
        response = requests.post(
            f"{API_BASE_URL}/reports/save",
            json={
                "user_id": user_id,
                "contract_name": filename,
                "analysis": analysis_result
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json().get("report_id")

        return None

    except Exception as e:
        print(f"Error saving report: {e}")
        return None


def download_analysis_json(analysis_result: dict, filename: str):
    """Prepare analysis for download"""
    json_str = json.dumps(analysis_result, indent=2)
    return json_str

def get_user_history(user_id):
    """Fetch the list of previous reports for the user"""
    try:
        response = requests.get(f"{API_BASE_URL}/reports/user/{user_id}")
        if response.status_code == 200:
            return response.json().get("reports", [])
    except Exception as e:
        st.sidebar.error(f"Error fetching history: {e}")
    return []

def load_full_report(report_id):
    """Fetch full report data and save to session state"""
    try:
        response = requests.get(f"{API_BASE_URL}/reports/full/{report_id}")
        if response.status_code == 200:
            data = response.json()
            st.session_state.selected_history = data["analysis"]
            st.session_state.selected_history["filename"] = data["contract_name"]
            st.session_state.selected_history["id"] = data["id"]
            return True
    except Exception as e:
        st.error(f"Error loading report: {e}")
    return False

def dashboard_page():
    st.markdown("<h1 class='main-title' style='margin-bottom:5px;'>Contract Intelligence Command Center</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9ca3af; font-weight:500;'>Multi-agent AI swarm ready for analysis.</p>", unsafe_allow_html=True)

    if not st.session_state.get("authenticated"):
        st.warning("⚠️ Please log in to access the dashboard")
        if st.button("Go to Login"):
            st.session_state.page = "auth"
            st.session_state.auth_nav_selection = "Login"
            st.rerun()
        return

    api_available, api_health = check_api_status()
    
    with st.sidebar:
        if api_available:
            st.success("⚡ AI Swarm Online")
            
            st.markdown("---")
            st.markdown("### 📜 Analysis History")
            
            user_id = st.session_state.user.get("id")
            if user_id:
                history = get_user_history(user_id) 
                
                if history:
                    for item in history:
                        date_str = item["created_at"][:10]
                        label = f"📄 {item['contract_name']} ({date_str})"
                        
                        if st.button(label, key=f"hist_{item['id']}", use_container_width=True):
                            if load_full_report(item["id"]):
                                st.rerun()
                else:
                    st.info("No previous reports found.")
        else:
            st.error("🔴 AI Backend Offline")
            st.info("💡 Tip: Start the backend on http://localhost:8000")
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
        st.markdown("<h5 style='text-align: center; color: white;'>Upload Documents</h5>", unsafe_allow_html=True)
        
        files = st.file_uploader("", type=["txt", "pdf", "docx"], accept_multiple_files=True, key="contract_uploader")
        
        if files:
            for f in files:
                original_name = f.name
                display_name = truncate_filename(original_name, max_length=45)
                size_kb = round(len(f.getvalue()) / 1024, 1)

                st.markdown(
                    f"""
                    <div style="background: rgba(15,20,45,0.85); border-radius: 14px; padding: 14px 18px; margin-top: 10px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 12px 30px rgba(0,0,0,0.6); overflow: hidden;">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div style="flex: 1; min-width: 0; overflow: hidden;">
                                <strong style="color:#e5edff; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{original_name}">📄 {display_name}</strong>
                                <span style="color:#9ca3af;font-size:0.85em;">{size_kb} KB</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("---")

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
            status.markdown(f"**📄 Processing:** `{truncate_filename(f.name, 50)}` with Multi-Agent AI System...")
            
            try:
                content = f.getvalue()
                try:
                    contract_text = content.decode("utf-8")
                except:
                    contract_text = content.decode("latin-1")
                
                if len(contract_text.strip()) < 100:
                    st.error(f"❌ File `{truncate_filename(f.name, 50)}` is too short (min 100 chars)")
                    continue
                
                success, result = analyze_contract_with_api(contract_text, tone)
                
                if success:
                    result["filename"] = f.name
                    results.append(result)
                    
                    if st.session_state.get("user") and st.session_state.user.get("id"):
                        report_id = save_report_to_db(
                            st.session_state.user["id"],
                            f.name,
                            result
                        )

                        if report_id:
                            result["id"] = report_id
                    
                    if 'analysis_history' not in st.session_state:
                        st.session_state.analysis_history = []
                    st.session_state.analysis_history.append(result)
                    
                    status.success(f"✅ Completed: `{truncate_filename(f.name, 50)}`")
                else:
                    st.error(f"❌ Analysis failed for `{truncate_filename(f.name, 50)}`: {result}")
                    
            except Exception as e:
                st.error(f"❌ Error processing `{truncate_filename(f.name, 50)}`: {str(e)}")
            
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
                filename_display = truncate_filename(result['filename'], 50)
                
                with st.expander(f"{icon} {filename_display} — {risk_text} RISK", expanded=True):
                    st.markdown(
                        f'<div class="risk-{overall_risk.lower()}" style="text-align:center; padding: 15px; border-radius: 10px; margin-bottom: 20px; background-color:{risk_color}33; border: 1px solid {risk_color};">'
                        f'<h3 style="margin:0; color: white;">{icon} {risk_text} RISK</h3>'
                        f'</div>', 
                        unsafe_allow_html=True
                    )
                    
                    col1, col2 = st.columns([3, 1])
                    with col2:
                        report_id = result.get('id')
                        if report_id:
                            try:
                                with st.spinner("Preparing PDF..."):
                                    response = requests.get(f"{API_BASE_URL}/reports/download/{report_id}")
                                    if response.status_code == 200:
                                        st.download_button(
                                            label="📥 Download PDF Report",
                                            data=response.content, 
                                            file_name=f"Analysis_Report_{report_id}.pdf",
                                            mime="application/pdf",
                                            key=f"dl_btn_{report_id}",
                                            use_container_width=True
                                        )
                            except Exception as e:
                                st.error(f"Connection error: {e}")

                    tab_summary, tab_agents, tab_clauses, tab_recs, tab_raw = st.tabs([
                        "📋 Summary", "🤖 Agents", "⚠️ Risks", "📝 Recommendations", "📊 Raw Data"
                    ])
                    
                    with tab_summary:
                        st.markdown("#### Overall Assessment")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Overall Risk", overall_risk.upper())
                        overall_conf = result.get('overall_assessment', {}).get('overall_confidence', 0)
                        col2.metric("Confidence", f"{overall_conf:.0%}")
                        proc_time = result.get('processing_time_seconds', 0)
                        col3.metric("Processing Time", f"{proc_time:.1f}s")
                    
                    with tab_agents:
                        st.markdown("#### Agent Reports")
                        agents = result.get('agent_assessments', {})
                        for agent_name in ['legal', 'compliance', 'finance', 'operations']:
                            agent_data = agents.get(agent_name, {})
                            if agent_data:
                                ai, at, ac = render_risk_indicator(agent_data.get('risk_level', 'unknown'))
                                st.markdown(f"**{ai} {agent_name.upper()} Agent**")
                                st.write(agent_data.get('enhanced_analysis', 'No detailed analysis provided.'))
                                st.markdown("---")
                    
                    with tab_clauses:
                        st.markdown("#### High-Risk Clauses")
                        high_risk_clauses = result.get('high_risk_clauses', [])
                        if high_risk_clauses:
                            for idx, clause in enumerate(high_risk_clauses, 1):
                                ci, ct, cc = render_risk_indicator(clause.get('risk_level', 'unknown'))
                                st.markdown(f"**{ci} Clause #{idx}**")
                                st.info(clause.get('clause', 'N/A'))
                        else:
                            st.success("✅ No high-risk clauses identified")
                    
                    with tab_recs:
                        st.markdown("#### Recommendations")
                        readable = result.get("human_readable_recommendations", "No recommendations available.")
                        st.text_area("AI Suggestions", value=readable, height=300, disabled=True, key=f"recs_{i}")

                    with tab_raw:
                        st.json(result)

    if "selected_history" in st.session_state:
        st.markdown("---")
        st.markdown("### 📂 Selected Previous Analysis")

        result = st.session_state.selected_history

        overall_risk = result.get("overall_assessment", {}).get("overall_risk", "unknown")
        icon, risk_text, risk_color = render_risk_indicator(overall_risk)

        st.markdown(
            f'<div style="padding: 15px; border-radius: 10px; '
            f'background-color:{risk_color}33; border: 1px solid {risk_color};">'
            f'<h3 style="margin:0; color:white;">{icon} {risk_text} RISK</h3>'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.markdown("#### Agent Recommendations")
        agents = result.get("agent_assessments", {})
        for agent, data in agents.items():
            st.markdown(f"**🤖 {agent.upper()}**")
            st.write(data.get("enhanced_analysis", "No analysis available"))
            st.markdown("---")
