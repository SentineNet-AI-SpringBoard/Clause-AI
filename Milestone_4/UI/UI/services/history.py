from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests


def _base_url() -> str:
    return (os.getenv("BACKEND_URL") or "http://127.0.0.1:8000").rstrip("/")


def _headers(token: str | None) -> Dict[str, str]:
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _safe_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return resp.text


def list_runs(*, token: str, limit: int = 8) -> List[Dict[str, Any]]:
    url = f"{_base_url()}/history"
    r = requests.get(url, params={"limit": int(limit)}, headers=_headers(token), timeout=30)
    if r.status_code >= 400:
        return []
    data = _safe_json(r)
    if isinstance(data, dict) and data.get("ok") and isinstance(data.get("runs"), list):
        return data["runs"]
    return []


def get_run(*, token: str, run_id: int) -> Optional[Dict[str, Any]]:
    url = f"{_base_url()}/history/{int(run_id)}"
    r = requests.get(url, headers=_headers(token), timeout=30)
    if r.status_code >= 400:
        return None
    data = _safe_json(r)
    if isinstance(data, dict) and data.get("ok"):
        run = data.get("run")
        return run if isinstance(run, dict) else None
    return None


def delete_run(*, token: str, run_id: int) -> bool:
    url = f"{_base_url()}/history/{int(run_id)}"
    r = requests.delete(url, headers=_headers(token), timeout=30)
    return r.status_code < 400


def save_run(
    *,
    token: str,
    mode: str,
    question: str,
    tone: str,
    run_all_agents: bool,
    no_evidence_threshold: float,
    filenames: List[str],
    results: List[Dict[str, Any]],
) -> Optional[int]:
    url = f"{_base_url()}/history/save"
    payload = {
        "mode": mode,
        "question": question,
        "tone": tone,
        "run_all_agents": bool(run_all_agents),
        "no_evidence_threshold": float(no_evidence_threshold),
        "filenames": list(filenames or []),
        "results": list(results or []),
    }
    r = requests.post(url, json=payload, headers=_headers(token), timeout=30)
    if r.status_code >= 400:
        return None
    data = _safe_json(r)
    if isinstance(data, dict) and data.get("ok") and data.get("id") is not None:
        try:
            return int(data["id"])
        except Exception:
            return None
    return None
