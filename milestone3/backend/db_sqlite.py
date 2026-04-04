from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


_BASE_DIR = Path(__file__).resolve().parents[1]
_OUTPUTS_DIR = _BASE_DIR / "outputs"
_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = Path(os.getenv("CLAUSEAI_BACKEND_DB_PATH", str(_OUTPUTS_DIR / "clauseai_backend.sqlite3")))
SESSION_TTL_HOURS = float(os.getenv("CLAUSEAI_SESSION_TTL_HOURS", "72"))


# Demo user seed is optional and only enabled when CLAUSEAI_DEMO_PASSWORD is set.
# This avoids hardcoding credentials into the repository (GitHub secret scanning will flag them).
DEMO_USERS: list[dict[str, str]] = [
    {"email": "legal.demo@example.com", "name": "Legal Demo", "role": "Legal"},
    {"email": "compliance.demo@example.com", "name": "Compliance Demo", "role": "Compliance"},
    {"email": "finance.demo@example.com", "name": "Finance Demo", "role": "Finance"},
    {"email": "operations.demo@example.com", "name": "Operations Demo", "role": "Operations"},
    {"email": "admin.demo@example.com", "name": "Admin Demo", "role": "Admin"},
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_now_iso() -> str:
    return _utc_now().isoformat()


def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    with _connect() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                avatar TEXT,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_email TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY(user_email) REFERENCES users(email)
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                created_at TEXT NOT NULL,
                mode TEXT NOT NULL,
                question TEXT NOT NULL,
                tone TEXT NOT NULL,
                run_all_agents INTEGER NOT NULL DEFAULT 0,
                no_evidence_threshold REAL NOT NULL,
                files_json TEXT NOT NULL,
                results_json TEXT NOT NULL,
                FOREIGN KEY(user_email) REFERENCES users(email)
            )
            """
        )
        con.commit()


def seed_demo_users() -> None:
    """Idempotently seed a small set of demo users (for local/dev UX)."""
    init_db()
    demo_password = (os.getenv("CLAUSEAI_DEMO_PASSWORD") or "").strip()
    if not demo_password:
        return
    for u in DEMO_USERS:
        try:
            create_user(
                email=u["email"],
                password=demo_password,
                name=u["name"],
                role=u.get("role") or "User",
            )
        except Exception:
            # Never block startup on demo seed.
            continue


def _norm_email(email: str) -> str:
    return (email or "").strip().lower()


def _new_salt() -> bytes:
    return os.urandom(16)


def _encode_salt(salt: bytes) -> str:
    return base64.b64encode(salt).decode("ascii")


def _decode_salt(salt_b64: str) -> bytes:
    return base64.b64decode((salt_b64 or "").encode("ascii"))


def _pbkdf2_hash(password: str, *, salt: bytes, iterations: int = 120_000) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", (password or "").encode("utf-8"), salt, iterations)
    return base64.b64encode(dk).decode("ascii")


def create_user(*, email: str, password: str, name: str, role: str = "User") -> Tuple[bool, str]:
    init_db()
    email_n = _norm_email(email)
    if not email_n or "@" not in email_n:
        return False, "Please enter a valid email address"
    if not (password or "").strip() or len(password) < 4:
        return False, "Password must be at least 4 characters"
    if not (name or "").strip():
        return False, "Name is required"

    salt = _new_salt()
    avatar = f"https://api.dicebear.com/7.x/initials/svg?seed={name.strip()}"

    with _connect() as con:
        exists = con.execute("SELECT 1 FROM users WHERE email = ?", (email_n,)).fetchone()
        if exists:
            return False, "An account with this email already exists"
        con.execute(
            """
            INSERT INTO users(email, name, role, avatar, password_salt, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email_n,
                name.strip(),
                (role or "User").strip() or "User",
                avatar,
                _encode_salt(salt),
                _pbkdf2_hash(password, salt=salt),
                _utc_now_iso(),
            ),
        )
        con.commit()
    return True, "Account created"


def _verify_password(password: str, *, salt_b64: str, expected_hash: str) -> bool:
    try:
        salt = _decode_salt(salt_b64)
        got = _pbkdf2_hash(password, salt=salt)
        return hmac.compare_digest(expected_hash or "", got)
    except Exception:
        return False


def get_user(email: str) -> Optional[Dict[str, Any]]:
    init_db()
    email_n = _norm_email(email)
    with _connect() as con:
        row = con.execute("SELECT email, name, role, avatar FROM users WHERE email = ?", (email_n,)).fetchone()
    return dict(row) if row else None


def login(*, email: str, password: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    init_db()
    email_n = _norm_email(email)
    with _connect() as con:
        row = con.execute(
            "SELECT email, name, role, avatar, password_salt, password_hash FROM users WHERE email = ?",
            (email_n,),
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        ok = _verify_password(password, salt_b64=d.get("password_salt") or "", expected_hash=d.get("password_hash") or "")
        if not ok:
            return None

        token = secrets.token_urlsafe(32)
        now = _utc_now()
        expires = now + timedelta(hours=SESSION_TTL_HOURS)
        con.execute(
            "INSERT INTO sessions(token, user_email, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token, email_n, now.isoformat(), expires.isoformat()),
        )
        con.commit()
        user = {"email": d.get("email"), "name": d.get("name"), "role": d.get("role"), "avatar": d.get("avatar")}
        return token, user


def _cleanup_expired_sessions(con: sqlite3.Connection) -> None:
    try:
        now = _utc_now().isoformat()
        con.execute("DELETE FROM sessions WHERE expires_at < ?", (now,))
    except Exception:
        return


def user_from_token(token: str) -> Optional[Dict[str, Any]]:
    init_db()
    tok = (token or "").strip()
    if not tok:
        return None
    with _connect() as con:
        _cleanup_expired_sessions(con)
        row = con.execute(
            """
            SELECT u.email, u.name, u.role, u.avatar
            FROM sessions s
            JOIN users u ON u.email = s.user_email
            WHERE s.token = ?
            """,
            (tok,),
        ).fetchone()
        con.commit()
    return dict(row) if row else None


def save_analysis_run(
    *,
    user_email: str,
    mode: str,
    question: str,
    tone: str,
    run_all_agents: bool,
    no_evidence_threshold: float,
    filenames: List[str],
    results: List[Dict[str, Any]],
) -> int:
    init_db()
    email_n = _norm_email(user_email)
    if not email_n:
        raise ValueError("Missing user_email")

    files_json = json.dumps(filenames or [], ensure_ascii=False)
    results_json = json.dumps(results or [], ensure_ascii=False)

    with _connect() as con:
        cur = con.execute(
            """
            INSERT INTO analysis_runs(
                user_email, created_at, mode, question, tone, run_all_agents,
                no_evidence_threshold, files_json, results_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email_n,
                _utc_now_iso(),
                (mode or "analysis").strip().lower(),
                question or "",
                (tone or "executive").strip().lower(),
                1 if run_all_agents else 0,
                float(no_evidence_threshold),
                files_json,
                results_json,
            ),
        )
        con.commit()
        return int(cur.lastrowid)


def list_analysis_runs(*, user_email: str, limit: int = 10) -> List[Dict[str, Any]]:
    init_db()
    email_n = _norm_email(user_email)
    with _connect() as con:
        rows = con.execute(
            """
            SELECT id, created_at, mode, question, tone, run_all_agents, no_evidence_threshold, files_json
            FROM analysis_runs
            WHERE user_email = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (email_n, int(limit)),
        ).fetchall()
    out: List[Dict[str, Any]] = []
    for r in rows:
        d = dict(r)
        try:
            d["files"] = json.loads(d.get("files_json") or "[]")
        except Exception:
            d["files"] = []
        out.append(d)
    return out


def get_analysis_run(*, user_email: str, run_id: int) -> Optional[Dict[str, Any]]:
    init_db()
    email_n = _norm_email(user_email)
    with _connect() as con:
        row = con.execute(
            "SELECT * FROM analysis_runs WHERE user_email = ? AND id = ?",
            (email_n, int(run_id)),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    try:
        d["files"] = json.loads(d.get("files_json") or "[]")
    except Exception:
        d["files"] = []
    try:
        d["results"] = json.loads(d.get("results_json") or "[]")
    except Exception:
        d["results"] = []
    return d


def delete_analysis_run(*, user_email: str, run_id: int) -> bool:
    init_db()
    email_n = _norm_email(user_email)
    with _connect() as con:
        cur = con.execute(
            "DELETE FROM analysis_runs WHERE user_email = ? AND id = ?",
            (email_n, int(run_id)),
        )
        con.commit()
        return cur.rowcount > 0
