import streamlit as st
import requests
import json
from datetime import datetime

# Define API Endpoint
API_URL = "http://127.0.0.1:8000/analyze-contract/"

# Page config with custom theme
st.set_page_config(
    page_title="Contract Analysis System", 
    page_icon="📄", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for BEAUTIFUL enhanced styling - FIXED EXPANDER TEXT
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container background */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Main title styling with gradient */
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Section headers */
    h2, h3 {
        color: #2d3748;
        font-weight: 700;
    }
    
    /* Card styling with shadow */
    .stExpander {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
        transition: all 0.3s ease;
    }
    
    .stExpander:hover {
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        transform: translateY(-2px);
    }
    
    /* Metric cards with gradient backgrounds */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #4a5568;
        font-weight: 600;
    }
    
    /* Risk badges with better colors */
    .risk-high {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
        font-size: 1.1rem;
    }
    
    .risk-medium {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #744210;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(252, 182, 159, 0.4);
        font-size: 1.1rem;
    }
    
    .risk-low {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #0d4d4d;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        display: inline-block;
        box-shadow: 0 4px 15px rgba(168, 237, 234, 0.4);
        font-size: 1.1rem;
    }
    
    /* Sidebar styling with vibrant gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        box-shadow: 4px 0 15px rgba(0,0,0,0.1);
    }
    
    /* Sidebar text - WHITE for contrast */
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #f7fafc !important;
    }
    
    /* FIXED: Sidebar expander content - make text visible */
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 8px;
        padding: 1rem;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderContent * {
        color: #2d3748 !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderContent strong {
        color: #667eea !important;
    }
    
    /* Sidebar expander header */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        color: white !important;
        font-weight: 600;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    /* Sidebar metrics - special styling */
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #ffd700 !important;
        font-size: 2rem !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #e2e8f0 !important;
    }
    
    /* Sidebar divider */
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.3);
        margin: 1.5rem 0;
    }
    
    /* Button styling with gradient */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5rem;
        font-weight: 700;
        font-size: 1.2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Info boxes with gradients */
    .info-box {
        background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%);
        border-left: 6px solid #0284c7;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 6px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    }
    
    .success-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 6px solid #10b981;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background: white;
        border: 3px dashed #cbd5e0;
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: #f7fafc;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f7fafc;
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #4a5568;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        border-radius: 10px;
        font-weight: 600;
        border: none;
        padding: 0.75rem 1.5rem;
        box-shadow: 0 4px 10px rgba(72, 187, 120, 0.3);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(72, 187, 120, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Header with custom styling
st.markdown('<h1 class="main-title">📄 Contract Analysis System</h1>', unsafe_allow_html=True)

# Description with icons and cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("### ⚖️ Legal")
    st.caption("Risk analysis")
with col2:
    st.markdown("### 📋 Compliance")
    st.caption("Regulatory checks")
with col3:
    st.markdown("### 💰 Finance")
    st.caption("Financial risks")
with col4:
    st.markdown("### ⚙️ Operations")
    st.caption("Operational feasibility")

st.markdown("---")

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("## 🧭 Navigation")
    st.info("📤 Upload contracts to begin analysis")
    
    st.markdown("---")
    
    # Statistics section
    st.markdown("## 📊 System Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Agents", "4", help="Legal, Compliance, Finance, Operations")
    with col2:
        st.metric("Risk Levels", "3", help="High, Medium, Low")
    
    st.markdown("---")
    
    # Quick help - FIXED VISIBILITY
    with st.expander("📖 Quick Guide"):
        st.markdown("""
        **How to use:**
        
        1️⃣ Upload one or more .txt contract files
        
        2️⃣ Select report tone
        
        3️⃣ Click Analyze
        
        4️⃣ Review results
        
        **File Requirements:**
        
        📄 Format: .txt
        
        📏 Min: 10 characters
        
        💾 Max: 5 MB
        """)
    
    st.markdown("---")
    st.markdown("**👤 Created by:** Misthi Maheshwari")
    st.markdown("**🔖 Version:** 1.0.0")
    st.markdown("**📅 Updated:** Jan 2026")

# Main content area
st.markdown("## 📤 Upload Contracts")

# File uploader
uploaded_files = st.file_uploader(
    "Drop your contract files here or click to browse",
    type=["txt"],
    accept_multiple_files=True,
    help="Upload one or more .txt contract files (max 5MB each)"
)

# Handle No File Case
if not uploaded_files or len(uploaded_files) == 0:
    # Enhanced empty state
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("### 👋 Welcome to Contract Analysis System")
    st.markdown("""
    Get started by uploading your contract files above. Our intelligent system will analyze:
    
    ⚖️ **Legal risks** and unfavorable clauses
    
    📋 **Compliance** issues and regulatory gaps
    
    💰 **Financial** terms and payment risks
    
    ⚙️ **Operational** feasibility and commitments
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🚀 Fast Analysis")
        st.write("Process multiple contracts in seconds with batch upload")
    with col2:
        st.markdown("### 🎯 Accurate Detection")
        st.write("AI-powered intelligent risk identification system")
    with col3:
        st.markdown("### 📊 Clear Reports")
        st.write("Easy-to-understand summaries and detailed breakdowns")
    
    st.markdown("---")
    
    # Requirements in expandable section
    with st.expander("📋 File Requirements & Supported Contracts"):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Requirements:**")
            st.markdown("- 📄 **Format:** Text files (.txt)")
            st.markdown("- 📏 **Min Size:** 10 characters")
            st.markdown("- 💾 **Max Size:** 5 MB per file")
            st.markdown("- 🔢 **Batch:** Multiple files supported")
            st.markdown("- 🎨 **Tones:** 4 report styles available")
        
        with col2:
            st.markdown("**Supported Contracts:**")
            st.markdown("✅ Service agreements")
            st.markdown("✅ Supply contracts")
            st.markdown("✅ Employment agreements")
            st.markdown("✅ Non-disclosure agreements")
            st.markdown("✅ Partnership contracts")

else:
    # Show uploaded files
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.success(f"✅ **{len(uploaded_files)} file(s) uploaded successfully**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # File details in collapsible
    with st.expander("📁 View uploaded files details"):
        for idx, file in enumerate(uploaded_files, 1):
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.write(f"**#{idx}**")
            with col2:
                st.write(f"📄 {file.name}")
            with col3:
                st.caption(f"{file.size} bytes")
    
    # Analysis Settings
    st.markdown("## ⚙️ Analysis Settings")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        tone = st.selectbox(
            "Select Report Tone",
            ["professional", "executive", "technical", "simple"],
            help="Choose how you want the report formatted",
            index=0
        )
    with col2:
        st.markdown("**Tone Preview:**")
        tone_descriptions = {
            "professional": "📊 Detailed & formal",
            "executive": "🎯 Concise & action-focused",
            "technical": "🔧 Technical & precise",
            "simple": "📝 Easy to understand"
        }
        st.info(tone_descriptions[tone])
    
    st.markdown("---")
    
    # Analyze button
    if 'analyzing' not in st.session_state:
        st.session_state.analyzing = False
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            f"🔍 Analyze {len(uploaded_files)} Contract(s)", 
            type="primary",
            disabled=st.session_state.analyzing,
            use_container_width=True
        )
    
    if analyze_button:
        st.session_state.analyzing = True
        
        # Store results
        all_results = []
        
        # Progress display
        st.markdown("## 🔄 Analysis in Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        MIN_CHARS = 10
        
        # Process files
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.markdown(f"**Analyzing:** `{uploaded_file.name}` ({idx + 1}/{len(uploaded_files)})")
            progress_bar.progress((idx) / len(uploaded_files))
            
            with st.spinner(f"Processing {uploaded_file.name}..."):
                try:
                    file_content = uploaded_file.read()
                    contract_text = file_content.decode('utf-8')
                    
                    file_size_bytes = len(file_content)
                    char_count = len(contract_text)
                    
                    if file_size_bytes > 5 * 1024 * 1024:
                        st.error(f"❌ **{uploaded_file.name}:** File too large (max 5MB)")
                        continue
                    
                    if char_count < MIN_CHARS:
                        st.error(f"❌ **{uploaded_file.name}:** Contract too short (min {MIN_CHARS} characters)")
                        continue
                    
                    files = {"file": (uploaded_file.name, file_content, "text/plain")}
                    params = {"tone": tone}
                    
                    response = requests.post(API_URL, files=files, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        result['filename'] = uploaded_file.name
                        result['analyzed_at'] = datetime.now().isoformat()
                        all_results.append(result)
                    else:
                        st.error(f"❌ **{uploaded_file.name}:** API Error {response.status_code}")
                        
                except Exception as e:
                    st.error(f"❌ **{uploaded_file.name}:** {str(e)}")
        
        progress_bar.progress(1.0)
        status_text.markdown("✅ **Analysis complete!**")
        st.session_state.analyzing = False
        
        if all_results:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.success(f"🎉 **Successfully analyzed {len(all_results)} contract(s)!**")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Sort by risk
            risk_order = {"high": 0, "medium": 1, "low": 2}
            all_results.sort(key=lambda x: risk_order.get(x['analysis']['overall_risk'], 3))
            
            # Summary table
            st.markdown("## 📊 Analysis Summary")
            
            summary_data = []
            for result in all_results:
                overall_risk = result['analysis']['overall_risk']
                
                risk_emoji = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }
                
                summary_data.append({
                    "Contract": result['filename'],
                    "Risk": f"{risk_emoji.get(overall_risk, '⚪')} {overall_risk.upper()}",
                    "Legal": result['analysis']['legal']['risk_level'].upper(),
                    "Compliance": result['analysis']['compliance']['risk_level'].upper(),
                    "Finance": result['analysis']['finance']['risk_level'].upper(),
                    "Operations": result['analysis']['operations']['risk_level'].upper(),
                    "Analyzed": result['analyzed_at'][:19].replace('T', ' ')
                })
            
            st.dataframe(summary_data, use_container_width=True, height=300)
            
            # Detailed results
            st.markdown("## 📋 Detailed Analysis Results")
            
            for result in all_results:
                overall_risk = result['analysis']['overall_risk']
                risk_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                
                if overall_risk == "high":
                    header_color = "🚨"
                    risk_class = "risk-high"
                elif overall_risk == "medium":
                    header_color = "📄"
                    risk_class = "risk-medium"
                else:
                    header_color = "✅"
                    risk_class = "risk-low"
                
                with st.expander(
                    f"{header_color} **{result['filename']}** - {risk_emoji.get(overall_risk, '⚪')} {overall_risk.upper()} Risk", 
                    expanded=(overall_risk == "high")
                ):
                    
                    # Risk badge
                    st.markdown(f'<div class="{risk_class}">Overall Risk: {overall_risk.upper()}</div>', unsafe_allow_html=True)
                    st.markdown("---")
                    
                    # Key metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📄 Contract", result['filename'][:15] + "..." if len(result['filename']) > 15 else result['filename'])
                    with col2:
                        st.metric("📅 Analyzed", result['analyzed_at'][:10])
                    with col3:
                        st.metric("📏 Size", f"{result['file_info']['size_bytes']} bytes")
                    with col4:
                        st.metric("🎨 Tone", result['report_tone'].title())
                    
                    st.markdown("---")
                    
                    # Tabs
                    tab1, tab2, tab3 = st.tabs(["📊 JSON Response", "📋 Formatted Report", "🔍 Detailed Analysis"])
                    
                    with tab1:
                        st.json(result)
                    
                    with tab2:
                        st.text_area(
                            "Report",
                            result['report'],
                            height=400,
                            disabled=True,
                            key=f"report_{result['filename']}"
                        )
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.download_button(
                                label="📥 Download JSON Report",
                                data=json.dumps(result, indent=2),
                                file_name=f"analysis_{result['filename']}.json",
                                mime="application/json",
                                key=f"download_{result['filename']}"
                            )
                        with col2:
                            st.download_button(
                                label="📄 Download Text Report",
                                data=result['report'],
                                file_name=f"report_{result['filename']}.txt",
                                mime="text/plain",
                                key=f"download_txt_{result['filename']}"
                            )
                    
                    with tab3:
                        # Agent cards
                        agents = ["legal", "compliance", "finance", "operations"]
                        agent_icons = {"legal": "⚖️", "compliance": "📋", "finance": "💰", "operations": "⚙️"}
                        
                        for agent_name in agents:
                            agent = result['analysis'][agent_name]
                            
                            with st.container():
                                st.markdown(f"### {agent_icons[agent_name]} {agent['agent']} Analysis")
                                
                                col1, col2 = st.columns([1, 3])
                                with col1:
                                    risk_level = agent['risk_level']
                                    if risk_level == "high":
                                        st.markdown('<div class="risk-high">HIGH RISK</div>', unsafe_allow_html=True)
                                    elif risk_level == "medium":
                                        st.markdown('<div class="risk-medium">MEDIUM RISK</div>', unsafe_allow_html=True)
                                    else:
                                        st.markdown('<div class="risk-low">LOW RISK</div>', unsafe_allow_html=True)
                                
                                with col2:
                                    st.write(f"**Status:** {agent['status']}")
                                
                                st.write(f"**Analysis:** {agent['analysis']}")
                                
                                if 'risks' in agent and agent['risks']:
                                    st.warning("**⚠️ Identified Risks:**")
                                    for risk in agent['risks']:
                                        st.write(f"• {risk}")
                                
                                if 'recommendations' in agent and agent['recommendations']:
                                    st.info("**💡 Recommendations:**")
                                    for rec in agent['recommendations']:
                                        st.write(f"• {rec}")
                                
                                st.markdown("---")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("© 2026 Contract Analysis System")
with col2:
    st.caption("Built with Streaamlit & FastAPI")
with col3:
    st.caption("Version 1.0.0 | Powered by AI")