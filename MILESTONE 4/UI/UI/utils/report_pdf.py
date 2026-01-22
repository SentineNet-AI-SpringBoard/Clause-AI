from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Tuple

from fpdf import FPDF


def _safe_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _pdf_text(text: str) -> str:
    """Convert arbitrary text into something core PDF fonts can render.

    We intentionally avoid bundling a TTF font to keep the project lightweight.
    Core fonts are latin-1 only, so we normalize/replace common unicode glyphs.
    """

    if not text:
        return ""

    replacements = {
        "\u2022": "-",  # bullet
        "\u2013": "-",  # en-dash
        "\u2014": "-",  # em-dash
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u00a0": " ",  # nbsp
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)

    # Ensure output is latin-1 representable.
    return text.encode("latin-1", errors="replace").decode("latin-1")


def make_pdf_filename(*, mode: str | None, run_id: Any | None) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    mode_s = (_safe_str(mode) or "analysis").strip().lower()
    rid = _safe_str(run_id).strip() or "run"
    return f"clauseai_report_{mode_s}_{rid}_{ts}.pdf"


def run_to_plaintext(run: Dict[str, Any]) -> str:
    run_id = run.get("id")
    mode = (run.get("mode") or "analysis").upper()
    created_at = _safe_str(run.get("created_at") or "")
    question = _safe_str(run.get("question") or "").strip()
    tone = _safe_str(run.get("tone") or "").strip()

    lines: List[str] = []
    lines.append("ClauseAI Report")
    lines.append("")
    if run_id is not None:
        lines.append(f"Run ID: {run_id}")
    if created_at:
        lines.append(f"Created at: {created_at}")
    lines.append(f"Mode: {mode}")
    if tone:
        lines.append(f"Tone: {tone}")
    if question:
        lines.append("")
        lines.append("Question:")
        lines.append(question)

    results = run.get("results") or []
    if isinstance(results, list) and results:
        lines.append("")
        lines.append("=" * 60)
        for idx, r in enumerate(results):
            if not isinstance(r, dict):
                continue
            filename = (_safe_str(r.get("filename")) or f"file_{idx}").strip()
            intent = _safe_str(r.get("intent") or "")
            no_evidence = r.get("no_evidence")
            evidence_score = r.get("evidence_score")
            overall_risk = (r.get("analysis") or {}).get("overall_risk") if isinstance(r.get("analysis"), dict) else None
            report = _safe_str(r.get("report") or "").strip()

            lines.append("")
            lines.append(f"FILE: {filename}")
            if intent:
                lines.append(f"Intent: {intent}")
            if overall_risk:
                lines.append(f"Overall risk: {overall_risk}")
            if no_evidence is True:
                lines.append(f"No evidence: true (score={evidence_score})")
            lines.append("")
            lines.append(report if report else "(No report text found for this file.)")
            lines.append("")
            lines.append("-" * 60)
    else:
        lines.append("")
        lines.append("(No results found in this run.)")

    return "\n".join(lines).strip() + "\n"


def run_to_pdf_bytes(run: Dict[str, Any]) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", size=12)
    text = _pdf_text(run_to_plaintext(run))

    # 6mm line height reads well on A4.
    pdf.multi_cell(0, 6, text)

    # fpdf2 uses latin-1 when core fonts are used; output as bytes.
    out = pdf.output(dest="S")
    if isinstance(out, (bytes, bytearray)):
        return bytes(out)
    return _safe_str(out).encode("latin-1", errors="replace")
