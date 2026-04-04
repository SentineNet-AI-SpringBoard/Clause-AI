from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional

import requests


BANNED_OUTPUT_TERMS = [
    "risk",
    "high risk",
    "medium risk",
    "low risk",
    "confidence",
    "executive",
    "executive summary",
    "overall",
    "legal",
    "compliance",
    "finance",
    "operations",
]


HEADING_FORBIDDEN_KEYWORDS = {
    # Prevent cross-domain leakage.
    "service availability": [
        "payment",
        "late",
        "interest",
        "invoice",
        "termination",
        "liability",
        "compliance",
    ],
    "termination": [
        "payment",
        "late",
        "interest",
        "invoice",
        "uptime",
        "availability",
        "sla",
        "liability",
        "compliance",
        "audit",
    ],
    "payment terms": [
        "liability",
        "limitation of liability",
    ],
    "late fees": [
        "liability",
        "limitation of liability",
    ],
    "data protection / privacy": [
        "payment",
        "late",
        "interest",
        "invoice",
        "termination",
        "uptime",
        "availability",
        "sla",
        "liability",
        "audit",
    ],
}


@dataclass(frozen=True)
class RewriteConfig:
    provider: str
    url: Optional[str] = None
    model: Optional[str] = None
    timeout_s: float = 20.0


def load_rewrite_config_from_env() -> RewriteConfig:
    provider = os.getenv("QA_REWRITE_PROVIDER", "none").strip().lower()
    url = os.getenv("QA_REWRITE_URL")
    model = os.getenv("QA_REWRITE_MODEL")
    timeout_s = float(os.getenv("QA_REWRITE_TIMEOUT_S", "20"))
    return RewriteConfig(provider=provider, url=url, model=model, timeout_s=timeout_s)


def _numbers_in(text: str) -> set[str]:
    return set(re.findall(r"\b\d+(?:\.\d+)?%?\b", text or ""))


def validate_rewrite(
    *,
    heading: str,
    source_clause: str,
    rewritten: str,
    max_chars: int = 220,
) -> Optional[str]:
    """Return sanitized rewrite if valid, else None."""

    s = " ".join((rewritten or "").split()).strip()
    if not s:
        return None
    if "\n" in s or "\r" in s:
        return None
    if len(s) > max_chars:
        return None

    low = s.lower()
    if any(term in low for term in BANNED_OUTPUT_TERMS):
        return None

    h = (heading or "").strip().lower()
    forbidden = []
    for key, kws in HEADING_FORBIDDEN_KEYWORDS.items():
        if key in h:
            forbidden.extend(kws)
    if forbidden and any(k in low for k in forbidden):
        return None

    # Prevent invented numbers/percentages.
    src_nums = _numbers_in(source_clause)
    out_nums = _numbers_in(s)
    if not out_nums.issubset(src_nums):
        return None

    # Avoid headings/bullet markers from model.
    s = s.lstrip("•-* ").strip()
    if not s:
        return None

    return s


def _extract_text_from_response(data: Any) -> Optional[str]:
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        for k in ("output_text", "text", "response", "content"):
            if isinstance(data.get(k), str) and data.get(k).strip():
                return data.get(k)
        # OpenAI-style
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            c0 = choices[0]
            if isinstance(c0, dict):
                msg = c0.get("message")
                if isinstance(msg, dict) and isinstance(msg.get("content"), str):
                    return msg.get("content")
                if isinstance(c0.get("text"), str):
                    return c0.get("text")
    return None


def rewrite_clause_to_bullet(
    *,
    question: str,
    heading: str,
    clause_text: str,
    config: RewriteConfig,
) -> Optional[str]:
    """Rewrite a single clause into a single clean bullet.

    IMPORTANT:
    - The clause_text is already filtered/approved by deterministic rules.
    - The LLM is used only to simplify language, not to add information.
    """

    if config.provider in {"", "none", "off", "disabled"}:
        return None

    if config.provider != "http":
        # Keep only HTTP provider for now to avoid heavy local deps.
        return None

    if not config.url:
        return None

    prompt = (
        "You are rewriting contract clauses into ONE short bullet.\n"
        "Rules (STRICT):\n"
        "- Use ONLY the provided clause text.\n"
        "- Do NOT add facts, do NOT infer obligations.\n"
        "- Do NOT mention risk, confidence, or analysis.\n"
        "- Output ONE line only (no headings, no extra bullets).\n\n"
        f"Heading: {heading}\n"
        f"Question: {question}\n"
        f"Clause: {clause_text}\n\n"
        "Return one short bullet sentence."
    )

    payload: Dict[str, Any] = {
        "prompt": prompt,
    }

    # Support Ollama-style, but keep generic.
    if config.model:
        payload["model"] = config.model

    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(config.url, data=json.dumps(payload), headers=headers, timeout=config.timeout_s)
    except Exception:
        return None

    if resp.status_code >= 400:
        return None

    try:
        data = resp.json()
    except Exception:
        data = resp.text

    text = _extract_text_from_response(data)
    if not text:
        return None

    # Some providers may return multi-line output; take first non-empty line.
    lines = [ln.strip() for ln in str(text).splitlines() if ln.strip()]
    if not lines:
        return None

    candidate = lines[0]
    return validate_rewrite(heading=heading, source_clause=clause_text, rewritten=candidate)
