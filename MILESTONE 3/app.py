import streamlit as st
import requests
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
API_URL = "http://127.0.0.1:8000/analyze"
MAX_FILE_SIZE_MB = 2

st.set_page_config(
    page_title="ClauseAI – Contract Risk Analyzer",
    layout="wide"
)

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("ClauseAI")
st.sidebar.info("Upload contracts to analyze legal risk")
st.sidebar.markdown("👤 **Developed by: Utsavshri**")

# -----------------------------
# MAIN TITLE
# -----------------------------
st.title("📄 ClauseAI – Contract Risk Analyzer")

st.write(
    """
Upload a legal contract and get:
- Legal risk analysis
- Compliance insights
- Financial risks
- Operational obligations
"""
)

# -----------------------------
# FILE UPLOAD
# -----------------------------
uploaded_files = st.file_uploader(
    "Upload Contract File(s)",
    type=["txt"],
    accept_multiple_files=True
)

contracts = []

if uploaded_files:
    for file in uploaded_files:
        size_mb = file.size / (1024 * 1024)

        if size_mb > MAX_FILE_SIZE_MB:
            st.error(f"{file.name} exceeds {MAX_FILE_SIZE_MB} MB limit")
            continue

        text = file.read().decode("utf-8").strip()

        if not text:
            st.warning(f"{file.name} is empty")
            continue

        contracts.append({
            "name": file.name,
            "text": text,
            "chars": len(text)
        })

# -----------------------------
# PREVIEW
# -----------------------------
if contracts:
    st.subheader("📂 Uploaded Contracts")

    for c in contracts:
        with st.expander(c["name"]):
            st.write(f"**Characters:** {c['chars']}")
            st.text_area(
                "Preview (read-only)",
                c["text"][:3000],
                height=200,
                disabled=True
            )

# -----------------------------
# ANALYZE BUTTON
# -----------------------------
analyze_clicked = st.button(
    "🔍 Analyze Contract(s)",
    disabled=not contracts
)

# -----------------------------
# ANALYSIS
# -----------------------------
results = []

if analyze_clicked:
    with st.spinner("Analyzing contracts..."):
        for c in contracts:
            try:
                response = requests.post(
                    API_URL,
                    json={"contract_text": c["text"]},
                    timeout=30
                )

                if response.status_code != 200:
                    st.error(f"Failed: {c['name']} — {response.text}")
                    continue

                data = response.json()

                results.append({
                    "name": c["name"],
                    "risk": data["overall_risk"],
                    "analysis": data["analysis"],
                    "report": data["report"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            except requests.exceptions.RequestException as e:
                st.error(f"API error for {c['name']}: {e}")

# -----------------------------
# RESULTS
# -----------------------------
if results:
    st.subheader("📊 Analysis Results")

    # Sort by risk severity
    risk_order = {"High": 0, "Medium": 1, "Low": 2}
    results.sort(key=lambda x: risk_order.get(x["risk"], 3))

    for r in results:
        color = "🔴" if r["risk"] == "High" else "🟠" if r["risk"] == "Medium" else "🟢"

        with st.expander(f"{color} {r['name']} — Risk: {r['risk']}"):
            st.caption(f"Analyzed at: {r['timestamp']}")

            tab1, tab2 = st.tabs(["📑 JSON Analysis", "🧾 Report"])

            with tab1:
                st.json(r["analysis"])

            with tab2:
                st.text(r["report"])

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.markdown(
    "<center>ClauseAI © 2026 | Academic Project</center>",
    unsafe_allow_html=True
)



