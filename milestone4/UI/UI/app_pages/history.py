from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

import streamlit as st

from services.history import delete_run, get_run, list_runs
from utils.report_pdf import make_pdf_filename, run_to_pdf_bytes


@st.cache_data(show_spinner=False, ttl=60)
def _get_run_cached(token: str, run_id: int) -> Optional[Dict[str, Any]]:
    # Cache avoids re-fetching all runs on each Streamlit rerun.
    return get_run(token=token, run_id=int(run_id))


def history_page():
    st.markdown("<h2 style='margin-bottom:5px;'>History</h2>", unsafe_allow_html=True)
    st.caption("Your saved Ask + Launch Analysis runs (stored in the backend database).")

    user = st.session_state.get("user") or {}
    token = (user.get("token") or "").strip() if isinstance(user, dict) else ""
    if not token:
        st.warning("Please login to view your history.")
        return

    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        mode_filter = st.selectbox("Mode", ["All", "ask", "analysis"], index=0)
    with c2:
        limit = st.slider("Max items", 5, 50, 15, 5)
    with c3:
        q = st.text_input("Search question", placeholder="type to filter by question text")

    try:
        runs = list_runs(token=token, limit=int(limit))
    except Exception:
        runs = []

    if mode_filter != "All":
        runs = [r for r in runs if (r.get("mode") or "").lower() == mode_filter]
    if q:
        qq = q.strip().lower()
        runs = [r for r in runs if qq in (r.get("question") or "").lower()]

    if not runs:
        st.info("No history entries match your filters yet.")
        return

    for r in runs:
        run_id = int(r.get("id"))
        created_at = (r.get("created_at") or "").replace("T", " ")[:19]
        mode = (r.get("mode") or "analysis").upper()
        files = r.get("files") or []
        question = (r.get("question") or "").strip()
        if len(question) > 140:
            question = question[:140] + "…"

        with st.expander(f"{created_at} — {mode} — {len(files)} file(s) :: {question}"):
            st.caption(f"Run ID: {run_id}")

            # Fetch run details once for downloads / preview.
            loaded = _get_run_cached(token, run_id)

            b1, b2, b3 = st.columns([2, 2, 2])
            with b1:
                if st.button("Open in Dashboard", key=f"history_open_{run_id}", use_container_width=True):
                    try:
                        loaded = get_run(token=token, run_id=run_id)
                        _get_run_cached.clear()
                    except Exception as e:
                        loaded = None
                        st.session_state["history_load_error"] = f"Failed to load saved analysis: {e}"

                    if not loaded:
                        st.session_state["history_load_error"] = (
                            st.session_state.get("history_load_error")
                            or "Failed to load saved analysis. Please ensure the backend is running and you are logged in."
                        )
                        st.session_state.page = "dashboard"
                        st.rerun()

                    results = loaded.get("results") or []
                    if (loaded.get("mode") or "").lower() == "ask":
                        st.session_state["answer_results"] = results
                        st.session_state.pop("report_results", None)
                    else:
                        st.session_state["report_results"] = results
                        st.session_state.pop("answer_results", None)
                    st.session_state["query_box_input"] = loaded.get("question") or ""
                    st.session_state.page = "dashboard"
                    st.rerun()
            with b2:
                if loaded:
                    pdf_bytes = run_to_pdf_bytes(loaded)
                    file_name = make_pdf_filename(mode=loaded.get("mode"), run_id=loaded.get("id"))
                    st.download_button(
                        "Download Report",
                        data=pdf_bytes,
                        file_name=file_name,
                        mime="application/pdf",
                        use_container_width=True,
                        key=f"history_dl_pdf_{run_id}",
                    )
                else:
                    st.download_button(
                        "Download Report",
                        data=b"",
                        file_name=make_pdf_filename(mode=mode, run_id=run_id),
                        mime="application/pdf",
                        use_container_width=True,
                        disabled=True,
                        key=f"history_dl_pdf_{run_id}",
                    )
            with b3:
                if st.button("Delete", key=f"history_delete_{run_id}", use_container_width=True):
                    delete_run(token=token, run_id=run_id)
                    _get_run_cached.clear()
                    st.rerun()
