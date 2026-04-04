from __future__ import annotations

import os
from typing import Any, Dict, Optional

import requests


def _normalize_tone(ui_tone: str) -> str:
    t = (ui_tone or "").strip().lower()
    # Backend supports: executive | simple
    if t in {"simple"}:
        return "simple"
    if t in {"executive"}:
        return "executive"
    # Map other UI tones to closest supported tone.
    if t in {"professional", "technical"}:
        return "executive"
    return "executive"


def _guess_content_type(filename: str) -> str:
    name = (filename or "").lower()
    if name.endswith(".pdf"):
        return "application/pdf"
    if name.endswith(".docx"):
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    return "text/plain"


class BackendContractAnalyzer:
    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        timeout_s: float = 180.0,
    ) -> None:
        self.base_url = (base_url or os.getenv("BACKEND_URL") or "http://127.0.0.1:8000").rstrip("/")
        self.timeout_s = float(timeout_s)

    def analyze_file(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        question: str,
        tone: str,
        no_evidence_threshold: float = 0.25,
        contract_id: Optional[str] = None,
        intent_override: Optional[str] = None,
        run_all_agents: bool = False,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/analyze"
        files = {"file": (filename, file_bytes, _guess_content_type(filename))}
        data: Dict[str, Any] = {
            "question": question,
            "tone": _normalize_tone(tone),
            "no_evidence_threshold": str(no_evidence_threshold),
        }
        if contract_id:
            data["contract_id"] = contract_id
        if intent_override:
            data["intent_override"] = intent_override
        if run_all_agents:
            # Only meaningful for Launch Analysis (risk_analysis/executive_review).
            data["run_all_agents"] = "true"

        try:
            r = requests.post(url, files=files, data=data, timeout=self.timeout_s)
        except Exception as e:
            return {"error": f"Failed to reach backend at {self.base_url}: {e}"}

        if r.status_code >= 400:
            return {"error": f"Backend error {r.status_code}", "detail": _safe_json(r), "status_code": r.status_code}
        return r.json()

    def analyze_text(
        self,
        *,
        contract_text: str,
        question: str,
        tone: str,
        no_evidence_threshold: float = 0.25,
        contract_id: Optional[str] = None,
        intent_override: Optional[str] = None,
        run_all_agents: bool = False,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/analyze_text"
        payload: Dict[str, Any] = {
            "contract_text": contract_text,
            "question": question,
            "tone": _normalize_tone(tone),
            "no_evidence_threshold": float(no_evidence_threshold),
        }
        if contract_id:
            payload["contract_id"] = contract_id
        if intent_override:
            payload["intent_override"] = intent_override
        if run_all_agents:
            payload["run_all_agents"] = True

        try:
            r = requests.post(url, json=payload, timeout=self.timeout_s)
        except Exception as e:
            return {"error": f"Failed to reach backend at {self.base_url}: {e}"}

        if r.status_code >= 400:
            return {"error": f"Backend error {r.status_code}", "detail": _safe_json(r), "status_code": r.status_code}
        return r.json()


def _safe_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return resp.text


# Backward-compatible alias used by dashboard.py
ContractAnalyzer = BackendContractAnalyzer