from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

import requests


def _base_url() -> str:
    return (os.getenv("BACKEND_URL") or "http://127.0.0.1:8000").rstrip("/")


def _safe_json(resp: requests.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return resp.text


def add_user(*, email: str, password: str, name: str, role: str = "User") -> Tuple[bool, str]:
    url = f"{_base_url()}/auth/register"
    try:
        r = requests.post(url, json={"email": email, "password": password, "name": name, "role": role}, timeout=30)
    except Exception as e:
        return False, f"Failed to reach backend at {_base_url()}: {e}"

    if r.status_code >= 400:
        detail = _safe_json(r)
        if isinstance(detail, dict) and detail.get("detail"):
            return False, str(detail.get("detail"))
        return False, f"Backend error {r.status_code}: {detail}"

    data = _safe_json(r)
    if isinstance(data, dict) and data.get("ok"):
        return True, data.get("message") or "Account created"
    return True, "Account created"


def verify_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    url = f"{_base_url()}/auth/login"
    try:
        r = requests.post(url, json={"email": email, "password": password}, timeout=30)
    except Exception:
        return None

    if r.status_code >= 400:
        return None

    data = _safe_json(r)
    if not isinstance(data, dict) or not data.get("ok"):
        return None

    token = data.get("token")
    user = data.get("user") or {}
    if not token or not isinstance(user, dict):
        return None
    # Store token in the user dict for easy access from UI.
    user["token"] = token
    return user
