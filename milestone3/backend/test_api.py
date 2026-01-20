from __future__ import annotations

from pathlib import Path
import time

import pytest
from fastapi.testclient import TestClient

from app import app


client = TestClient(app)

_FALLBACK_SAMPLE_CONTRACT = """
MASTER SERVICES AGREEMENT

1. Payment Terms: Customer will pay within 15 days of invoice.
2. Late Fees: Late payments accrue interest at 1.5% per month.
3. Termination: Either party may terminate for material breach with 30 days cure.
4. Liability: Liability is capped at fees paid, except for uncapped confidentiality breach.
5. SLA: Uptime commitment is 99.9%. Service credits apply if uptime falls below 99.9%.
6. Audit: Customer may audit security controls annually.
""".strip()


def _load_sample_contract_bytes() -> bytes:
    p = Path(__file__).resolve().with_name("sample_contract.txt")
    if p.exists():
        return p.read_bytes()
    return _FALLBACK_SAMPLE_CONTRACT.encode("utf-8")


def _post(file_bytes: bytes, filename: str, question: str, tone: str = "executive"):
    return client.post(
        "/analyze",
        files={"file": (filename, file_bytes, "text/plain")},
        data={"question": question, "tone": tone, "no_evidence_threshold": "0.25"},
    )


@pytest.fixture(scope="session")
def sample_bytes() -> bytes:
    return _load_sample_contract_bytes()


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_empty_file_400():
    r = _post(b"", "empty.txt", "What are payment terms?")
    assert r.status_code == 400


def test_empty_question_400(sample_bytes: bytes):
    r = client.post(
        "/analyze",
        files={"file": ("c.txt", sample_bytes, "text/plain")},
        data={"question": "   ", "tone": "executive"},
    )
    assert r.status_code == 400


def test_executive_tone_report(sample_bytes: bytes):
    # No explicit "risk/review/analysis" -> intent defaults to fact_summary.
    r = _post(sample_bytes, "contract.txt", "Summarize payment terms and late fees", "executive")
    assert r.status_code == 200
    j = r.json()
    assert j.get("intent") == "fact_summary"
    report = j.get("report") or ""
    assert "CONTRACT ANALYSIS REPORT" not in report
    assert "Executive Summary" not in report
    assert "RISK" not in report
    assert "•" in report
    # Clause mapping discipline: do not leak limitation of liability into other headings.
    low = report.lower()
    assert "liability" not in low
    # Semantic correctness: show evidence of both requested headings.
    assert "payment terms" in low
    assert "late fees" in low


def test_explicit_risk_analysis_produces_multi_agent_report(sample_bytes: bytes):
    q = "Provide a risk analysis of payment terms and late fees"
    r = _post(sample_bytes, "contract.txt", q, "executive")
    assert r.status_code == 200
    j = r.json()
    assert j.get("intent") == "risk_analysis"
    report = j.get("report") or ""
    low = report.lower()
    assert "contract analysis report" in low
    assert "executive summary" in low
    # Do not repeat the user's original question.
    assert q.lower() not in low
    # No generic filler from older template.
    assert "route to approval" not in low
    assert "negotiate" not in low
    assert "confidence" not in low
    # Evidence/points must be grounded in clause language.
    assert "15" in report  # payment window from contract
    assert "1.5" in report  # interest rate from contract


def test_risk_analysis_payment_late_is_targeted_to_finance(sample_bytes: bytes):
    q = "Analyze payment terms and late fees"
    r = client.post(
        "/analyze",
        files={"file": ("contract.txt", sample_bytes, "text/plain")},
        data={
            "question": q,
            "tone": "executive",
            "no_evidence_threshold": "0.25",
            "intent_override": "risk_analysis",
        },
    )
    assert r.status_code == 200
    j = r.json()
    assert j.get("intent") == "risk_analysis"

    report = (j.get("report") or "").lower()
    # Targeted analysis should not include unrelated sections.
    assert "\nfinance\n" in report
    assert "\nlegal\n" not in report
    assert "\ncompliance\n" not in report
    assert "\noperations\n" not in report
    # And should not leak unrelated topics.
    assert "termination" not in report
    assert "liability" not in report


def test_risk_analysis_run_all_agents_forces_all_sections(sample_bytes: bytes):
    r = client.post(
        "/analyze",
        files={"file": ("contract.txt", sample_bytes, "text/plain")},
        data={
            "question": "Analyze payment terms and late fees",
            "tone": "executive",
            "no_evidence_threshold": "0.25",
            "intent_override": "risk_analysis",
            "run_all_agents": "true",
        },
    )
    assert r.status_code == 200
    j = r.json()
    assert j.get("intent") == "risk_analysis"

    selected = ((j.get("agent_analysis") or {}).get("selected_agents") or [])
    assert set(selected) == {"legal", "compliance", "finance", "operations"}

    rep = (j.get("report") or "").lower()
    assert "\nlegal\n" in rep
    assert "\ncompliance\n" in rep
    assert "\nfinance\n" in rep
    assert "\noperations\n" in rep


def test_intent_override_forces_risk_analysis(sample_bytes: bytes):
    r = client.post(
        "/analyze",
        files={"file": ("contract.txt", sample_bytes, "text/plain")},
        data={
            "question": "Summarize payment terms and late fees",
            "tone": "executive",
            "no_evidence_threshold": "0.25",
            "intent_override": "risk_analysis",
        },
    )
    assert r.status_code == 200
    j = r.json()
    assert j.get("intent") == "risk_analysis"
    assert "CONTRACT ANALYSIS REPORT" in (j.get("report") or "")


def test_simple_tone_report(sample_bytes: bytes):
    # Still fact_summary by default; tone does not change intent.
    r = _post(sample_bytes, "contract.txt", "Summarize SLA and service credits", "simple")
    assert r.status_code == 200
    rep = r.json().get("report") or ""
    assert "CONTRACT ANALYSIS REPORT" not in rep
    assert "•" in rep


def test_service_availability_fact_summary_filtered(sample_bytes: bytes):
    q = "What service availability is guaranteed?"
    r = _post(sample_bytes, "contract.txt", q, "executive")
    assert r.status_code == 200
    j = r.json()
    assert j.get("intent") == "fact_summary"
    rep = (j.get("report") or "").lower()

    # Must not auto-generate executive report/risk sections.
    assert "contract analysis report" not in rep
    assert "risk level" not in rep
    assert "executive summary" not in rep

    # Must include Service Availability heading and uptime commitment.
    assert "service availability" in rep
    assert "99.9" in rep

    # Must exclude unrelated domains.
    assert "payment terms" not in rep
    assert "late fees" not in rep
    assert "termination" not in rep
    assert "compliance" not in rep
    assert "liability" not in rep


def test_service_availability_in_analysis_sets_operations_low(sample_bytes: bytes):
    q = "Provide a risk analysis of service availability"
    r = _post(sample_bytes, "contract.txt", q, "executive")
    assert r.status_code == 200
    assert r.json().get("intent") == "risk_analysis"
    report = r.json().get("report") or ""
    low = report.lower()
    assert "operations" in low
    # Must not mark Operations as N/A if availability/uplink uptime exists.
    assert "risk level: low" in low
    assert "99.9" in low


def test_no_evidence_true_for_unrelated_question(sample_bytes: bytes):
    r = _post(sample_bytes, "contract.txt", "What is the warranty period for hardware?", "executive")
    assert r.status_code == 200
    assert r.json().get("no_evidence") is True


def test_high_risk_question_returns_200(sample_bytes: bytes):
    r = _post(sample_bytes, "contract.txt", "Is there uncapped liability?", "executive")
    assert r.status_code == 200


def test_termination_question_returns_200(sample_bytes: bytes):
    r = _post(sample_bytes, "contract.txt", "Explain termination for breach", "simple")
    assert r.status_code == 200


def test_termination_fact_summary_isolated(sample_bytes: bytes):
    q = "Explain termination rights under this agreement"
    r = _post(sample_bytes, "contract.txt", q, "executive")
    assert r.status_code == 200
    j = r.json()
    assert j.get("intent") == "fact_summary"
    rep = (j.get("report") or "").lower()

    # Must include termination heading/content.
    assert "termination" in rep

    # Must explicitly exclude unrelated domains for termination questions.
    assert "payment terms" not in rep
    assert "late fees" not in rep
    assert "service levels" not in rep
    assert "audit" not in rep
    assert "compliance" not in rep
    assert "liability" not in rep


def test_large_input_returns_200(sample_bytes: bytes):
    big = (sample_bytes.decode("utf-8", errors="ignore") + "\n" + ("Additional clause text. " * 500)).encode("utf-8")
    r = _post(big, "big.txt", "Summarize audit rights", "executive")
    assert r.status_code == 200


def test_auth_and_history_roundtrip(sample_bytes: bytes):
    email = f"testuser_{int(time.time())}@example.com"
    password = "pass1234"
    name = "Test User"

    r = client.post("/auth/register", json={"email": email, "password": password, "name": name})
    assert r.status_code == 200
    assert r.json().get("ok") is True

    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200
    j = r.json()
    assert j.get("ok") is True
    token = j.get("token")
    assert token

    headers = {"Authorization": f"Bearer {token}"}
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    assert (r.json().get("user") or {}).get("email") == email

    # Save a history run
    payload = {
        "mode": "ask",
        "question": "Summarize payment terms",
        "tone": "executive",
        "run_all_agents": False,
        "no_evidence_threshold": 0.25,
        "filenames": ["contract.txt"],
        "results": [{"filename": "contract.txt", "intent": "fact_summary", "report": "• Payment Terms: within 15 days"}],
    }
    r = client.post("/history/save", json=payload, headers=headers)
    assert r.status_code == 200
    run_id = r.json().get("id")
    assert isinstance(run_id, int)

    r = client.get("/history", headers=headers)
    assert r.status_code == 200
    runs = (r.json().get("runs") or [])
    assert any(int(x.get("id")) == run_id for x in runs)

    r = client.get(f"/history/{run_id}", headers=headers)
    assert r.status_code == 200
    run = r.json().get("run") or {}
    assert run.get("id") == run_id
    assert run.get("mode") == "ask"
    assert run.get("question") == "Summarize payment terms"

    r = client.delete(f"/history/{run_id}", headers=headers)
    assert r.status_code == 200
    assert r.json().get("ok") is True



def test_contract_id_override(sample_bytes: bytes):
    r = client.post(
        "/analyze",
        files={"file": ("contract.txt", sample_bytes, "text/plain")},
        data={
            "question": "Summarize payment terms",
            "tone": "executive",
            "contract_id": "uploaded_contract",
            "no_evidence_threshold": "0.25",
        },
    )
    assert r.status_code == 200
    assert r.json().get("contract_id") == "uploaded_contract"
