from __future__ import annotations

import asyncio
import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


def _maybe_load_sentence_transformer():
    """Lazy-load SentenceTransformer.

    IMPORTANT: On some Windows setups, importing sentence-transformers/transformers
    can cause a hard interpreter crash (access violation) due to native deps.
    To keep the API reliable, this is opt-in via USE_SENTENCE_TRANSFORMERS=1.
    """

    if os.getenv("USE_SENTENCE_TRANSFORMERS", "0").strip() not in {"1", "true", "True", "yes", "YES"}:
        return None
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore

        return SentenceTransformer
    except Exception:
        return None


# Base folder for Milestone 3
MILESTONE3_DIR = Path(__file__).resolve().parents[1]
OUTPUTS_DIR = MILESTONE3_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

MEMORY_DIR = OUTPUTS_DIR / "api_memory"
MEMORY_DIR.mkdir(parents=True, exist_ok=True)


# Terms used for extracting/highlighting "high risk" evidence snippets.
# This is intentionally broader than the actual risk scoring.
HIGH_RISK_TERMS = [
    "penalt",
    "late fee",
    "interest",
    "termination",
    "breach",
    "indemn",
    "liability",
    "service credit",
    "audit",
    "privacy",
    "security",
    "incident",
    "retention",
    "subprocessor",
    "uncapped",
    "unlimited",
    "limitation of liability",
]

# Terms used for *risk scoring* (disciplined).
# Common clauses are not automatically HIGH; only severe one-sided terms are.
SEVERE_RISK_TERMS = [
    "uncapped",
    "unlimited",
]

MODERATE_RISK_TERMS = [
    "limitation of liability",
    "indemn",
    "privacy",
    "security",
    "incident",
    "subprocessor",
    "retention",
]

COMMON_RISK_TERMS = [
    "termination",
    "breach",
    "late fee",
    "interest",
    "service credit",
    "sla",
    "uptime",
]

RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "unknown": 1}


def detect_intent(question: str) -> str:
    """Determine user intent from the question.

    POSSIBLE INTENTS:
    - fact_summary
    - clause_extraction
    - qa
    - risk_analysis
    - executive_review

    DEFAULT:
    - If the user did NOT explicitly ask for "risk", "review", or "analysis",
      assume intent = fact_summary.
    """

    q = (question or "").strip().lower()
    if not q:
        return "fact_summary"

    # NON-NEGOTIABLE intent discipline:
    # - Default to fact_summary for factual prompts (Explain/Summarize/What are/Describe/List)
    # - Only enter risk_analysis when the user explicitly requests "risk" or "analysis"
    factual_triggers = ["explain", "summarize", "what", "what are", "what is", "describe", "list"]
    is_factual_prompt = any(q.startswith(t) or f" {t} " in f" {q} " for t in factual_triggers)

    wants_risk = any(k in q for k in ["risk", "riskiness", "red flag", "red flags"])
    wants_analysis = "analysis" in q and not any(k in q for k in ["data analysis", "statistical analysis"])

    if wants_risk or wants_analysis:
        return "risk_analysis"
    if is_factual_prompt:
        return "fact_summary"

    if any(k in q for k in ["extract", "clause", "section", "provide the clause", "show the clause", "quote"]):
        return "clause_extraction"

    # Heuristic QA detection.
    if re.match(r"^(what|when|who|where|why|how)\b", q):
        return "qa"

    return "fact_summary"


def _heading_for_fact_summary(question: str) -> str:
    q = (question or "").lower()
    if any(k in q for k in ["service availability", "availability", "uptime", "scheduled maintenance", "% of the time"]):
        return "Service Availability"
    if any(k in q for k in ["payment", "invoice", "due"]):
        if any(k in q for k in ["late", "interest", "penalt", "fee"]):
            return "Payment Terms and Late Fees"
        return "Payment Terms"
    if any(k in q for k in ["termination", "breach", "cure"]):
        return "Termination"
    if any(k in q for k in ["liability", "indemn", "cap"]):
        return "Liability"
    if any(k in q for k in ["sla", "uptime", "service credit"]):
        return "Service Levels (SLA)"
    if any(k in q for k in ["audit"]):
        return "Audit Rights"
    return "Answer"


def format_fact_summary_report(question: str, matches: List[RetrievalMatch]) -> str:
    """Section A answer formatting (fact_summary/qa).

    Rules:
    - Include only clauses that answer the question
    - No risk/confidence language
    - Clean bullets, no paragraph dumps
    """

    sa = build_sanitized_answer(question, matches)
    sections = sa.get("sections") or []
    if not sections:
        return "Answer\n• No relevant evidence found in the provided document for this question."

    # Optional LLM rewrite pass (safe, evidence-locked).
    # Disabled by default. Enable via:
    # - QA_REWRITE_PROVIDER=http
    # - QA_REWRITE_URL=<your local endpoint>
    # - QA_REWRITE_MODEL=<optional model name>
    try:
        from qa_llm_rewriter import load_rewrite_config_from_env, rewrite_clause_to_bullet  # type: ignore

        cfg = load_rewrite_config_from_env()
        if cfg.provider not in {"", "none", "off", "disabled"}:
            for sec in sections:
                heading = (sec.get("heading") or "Answer").strip()
                new_bullets: List[str] = []
                for b in (sec.get("bullets") or []):
                    rewritten = rewrite_clause_to_bullet(
                        question=question,
                        heading=heading,
                        clause_text=b,
                        config=cfg,
                    )
                    new_bullets.append(rewritten or b)
                sec["bullets"] = new_bullets
    except Exception:
        # Any failure keeps deterministic bullets.
        pass

    out: List[str] = []
    for sec in sections:
        heading = (sec.get("heading") or "Answer").strip()
        bullets = sec.get("bullets") or []
        if not bullets:
            continue
        out.append(heading)
        for b in bullets:
            out.append(f"• {b}")
        out.append("")
    return "\n".join(out).strip()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_contract_id(contract_text: str) -> str:
    """Deterministic id for an uploaded contract body."""
    h = hashlib.sha256((contract_text or "").encode("utf-8", errors="ignore")).hexdigest()
    return f"uploaded_{h[:12]}"


def chunk_text(text: str, *, chunk_size: int = 900, overlap: int = 120) -> List[str]:
    t = " ".join((text or "").split())
    if not t:
        return []
    if chunk_size <= 0:
        return [t]

    out: List[str] = []
    i = 0
    while i < len(t):
        out.append(t[i : i + chunk_size])
        if i + chunk_size >= len(t):
            break
        i = max(0, i + chunk_size - overlap)
    return out


def cosine_sim_matrix(query_vec: np.ndarray, doc_vecs: np.ndarray) -> np.ndarray:
    q = query_vec.astype(np.float32)
    d = doc_vecs.astype(np.float32)
    qn = np.linalg.norm(q) + 1e-12
    dn = np.linalg.norm(d, axis=1) + 1e-12
    return (d @ q) / (dn * qn)


@dataclass
class RetrievalMatch:
    score: float
    chunk_index: int
    text: str


class LocalRAGIndex:
    """Minimal local RAG index (in-memory).

    Prefers SentenceTransformers embeddings when available; falls back to a
    deterministic hashing embedder (no torch) when not.
    """

    def __init__(self, *, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.model = None
        self.embedder_name = "hashing"

        self._hash_dim = 384
        self._hash_salt = "m3"

        SentenceTransformer = _maybe_load_sentence_transformer()
        if SentenceTransformer is not None:
            try:
                self.model = SentenceTransformer(model_name)
                self.embedder_name = f"sentence-transformers:{model_name}"
            except Exception:
                # Any failure -> fallback.
                self.model = None
                self.embedder_name = "hashing"
        self.chunks: List[str] = []
        self.vectors: Optional[np.ndarray] = None

    def _hash_embed(self, texts: List[str], *, normalize_embeddings: bool = True) -> np.ndarray:
        dim = int(self._hash_dim)
        out = np.zeros((len(texts), dim), dtype=np.float32)

        for row_idx, text in enumerate(texts):
            tokens = re.findall(r"[a-z0-9]+", (text or "").lower())
            if not tokens:
                continue

            for tok in tokens:
                h = hashlib.md5(f"{self._hash_salt}:{tok}".encode("utf-8", errors="ignore")).digest()
                idx = int.from_bytes(h[:2], "little") % dim
                sign = 1.0 if (h[2] & 1) == 0 else -1.0
                out[row_idx, idx] += sign

        if normalize_embeddings:
            norms = np.linalg.norm(out, axis=1, keepdims=True) + 1e-12
            out = out / norms
        return out

    def encode(self, texts: List[str], *, normalize_embeddings: bool = True) -> np.ndarray:
        if self.model is not None:
            vecs = self.model.encode(texts, normalize_embeddings=normalize_embeddings)
            return np.asarray(vecs, dtype=np.float32)
        return self._hash_embed(texts, normalize_embeddings=normalize_embeddings)

    def build(self, contract_text: str) -> None:
        self.chunks = chunk_text(contract_text)
        if not self.chunks:
            self.vectors = None
            return
        self.vectors = self.encode(self.chunks, normalize_embeddings=True)

    def query(self, query_text: str, *, top_k: int = 5) -> List[RetrievalMatch]:
        if not (query_text or "").strip() or self.vectors is None or not self.chunks:
            return []
        qv = self.encode([query_text], normalize_embeddings=True)[0]
        sims = cosine_sim_matrix(np.asarray(qv, dtype=np.float32), self.vectors)
        idxs = np.argsort(-sims)[: max(1, int(top_k))]
        out: List[RetrievalMatch] = []
        for i in idxs:
            out.append(RetrievalMatch(score=float(sims[int(i)]), chunk_index=int(i), text=self.chunks[int(i)]))
        return out


def infer_risk_from_text(text: str) -> str:
    t = (text or "").lower()
    if any(term in t for term in SEVERE_RISK_TERMS):
        return "high"
    if any(term in t for term in MODERATE_RISK_TERMS):
        return "medium"
    if any(term in t for term in COMMON_RISK_TERMS):
        return "medium"
    return "low"


def confidence_from_matches(matches: List[RetrievalMatch]) -> Optional[float]:
    if not matches:
        return None
    return float(sum(m.score for m in matches) / len(matches))


def _extract_key_sentences(text: str, *, keywords: List[str], max_sentences: int = 3) -> List[str]:
    t = " ".join((text or "").split())
    if not t:
        return []

    # Very lightweight sentence splitting.
    parts = [p.strip() for p in re.split(r"(?<=[\.!?])\s+", t) if p.strip()]
    if not parts:
        parts = [t]

    kws = [k.lower() for k in keywords if (k or "").strip()]
    scored: List[Tuple[int, str]] = []
    for p in parts:
        pl = p.lower()
        score = sum(1 for k in kws if k in pl)
        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: (-x[0], len(x[1])))
    out: List[str] = []
    seen: set[str] = set()
    for _, sent in scored:
        key = sent.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(sent[:300])
        if len(out) >= max_sentences:
            break
    return out


def _question_keywords(question: str) -> List[str]:
    tokens = re.findall(r"[a-z0-9]+", (question or "").lower())
    stop = {
        "what",
        "are",
        "is",
        "the",
        "a",
        "an",
        "and",
        "or",
        "of",
        "to",
        "in",
        "for",
        "on",
        "with",
        "about",
        "please",
        "explain",
        "summarize",
        "terms",
        "clause",
        "contract",
        "agreement",
    }
    kws = [t for t in tokens if t not in stop and len(t) >= 3]
    return kws or tokens[:8]


def _requested_topics(question: str) -> List[str]:
    q = (question or "").lower()
    topics: List[str] = []
    if any(k in q for k in ["privacy", "data protection", "personal data", "customer data"]):
        topics.append("privacy")
    if any(k in q for k in ["service availability", "availability", "uptime", "scheduled maintenance", "% of the time"]):
        topics.append("availability")
    if any(k in q for k in ["payment", "invoice", "due", "pay"]):
        topics.append("payment")
    if any(k in q for k in ["late", "interest", "late fee", "penalt", "fee"]):
        topics.append("late")
    if any(k in q for k in ["termination", "breach", "cure"]):
        topics.append("termination")
    if any(k in q for k in ["liability", "indemn", "cap"]):
        topics.append("liability")
    if any(k in q for k in ["sla", "uptime", "service credit"]):
        topics.append("sla")
    if "audit" in q:
        topics.append("audit")
    return topics


def _should_run_all_agents(question: str) -> bool:
    q = (question or "").lower()
    # Broad review prompts => run all agents.
    broad_markers = [
        "overall",
        "full",
        "entire",
        "whole",
        "end-to-end",
        "all clauses",
        "all risks",
        "key risks",
        "general risks",
        "review the contract",
        "review this agreement",
        "comprehensive",
        "complete analysis",
    ]
    return any(m in q for m in broad_markers)


def select_agents_for_question(question: str) -> List[str]:
    """Pick only the agents relevant to the question.

    This improves speed and avoids unrelated sections.
    """

    all_agents = ["legal", "compliance", "finance", "operations"]
    if _should_run_all_agents(question):
        return all_agents

    q = (question or "").lower()
    topics = _requested_topics(question)
    selected: List[str] = []

    # Explicit agent request routing (from UI multi-select prompt)
    # The UI generates prompts like: "review Legal, Finance aspects specifically"
    # We prioritize these explicit instructions.
    explicit_matches = False
    if "legal" in q and "review" in q:
        selected.append("legal")
        explicit_matches = True
    if "finance" in q and "review" in q:
        selected.append("finance")
        explicit_matches = True
    if "compliance" in q and "review" in q:
        selected.append("compliance")
        explicit_matches = True
    if ("operations" in q or "ops" in q) and "review" in q:
        selected.append("operations")
        explicit_matches = True
    
    # If explicit agents were found in a "review" context, trust that signal.
    # Otherwise, fall back to topic inference.
    if explicit_matches:
        return list(set(selected))

    # Topic-based routing
    if any(t in topics for t in ["payment", "late"]):
        selected.append("finance")
    if any(t in topics for t in ["termination", "liability"]):
        selected.append("legal")
    if any(t in topics for t in ["privacy", "audit"]):
        selected.append("compliance")
    if any(t in topics for t in ["availability", "sla"]):
        selected.append("operations")

    # Keyword-based fallback for common compliance/ops concepts.
    if any(k in q for k in ["gdpr", "hipaa", "privacy", "data protection", "security", "breach", "incident", "retention", "subprocessor", "audit"]):
        if "compliance" not in selected:
            selected.append("compliance")
    if any(k in q for k in ["sla", "uptime", "availability", "service availability", "service credits", "support", "uptime"]):
        if "operations" not in selected:
            selected.append("operations")

    # If the question doesn't map cleanly, default to all agents.
    return selected or all_agents


def _topic_heading(topic: str) -> str:
    return {
        "privacy": "Data Protection / Privacy",
        "availability": "Service Availability",
        "payment": "Payment Terms",
        "late": "Late Fees",
        "termination": "Termination",
        "liability": "Limitation of Liability",
        "sla": "Service Levels (SLA)",
        "audit": "Audit Rights",
    }.get(topic, "Answer")


def _split_into_clause_candidates(text: str) -> List[str]:
    t = " ".join((text or "").split())
    if not t:
        return []
    # Split on numbered headings like "1. Payment Terms ... 2. Late Fees ...".
    parts = re.split(r"(?=\b\d+\.\s+[A-Z])", t)
    parts = [p.strip() for p in parts if p.strip()]
    if len(parts) <= 1:
        parts = [p.strip() for p in re.split(r"(?<=[\.!?;])\s+", t) if p.strip()]
    return parts


def _split_into_atomic_statements(text: str) -> List[str]:
    """Split a clause into atomic statements for bullet rendering.

    Prevents concatenating multiple meanings into one bullet.
    """
    t = " ".join((text or "").split()).strip()
    if not t:
        return []
    parts = [p.strip() for p in re.split(r"(?<=[\.!?;])\s+", t) if p.strip()]
    return parts or [t]


def _normalize_clause(clause: str) -> str:
    c = " ".join((clause or "").split()).strip()
    c = re.sub(r"^\d+\.\s+", "", c).strip()
    c = re.sub(
        r"^(Payment Terms|Late Fees\s*/\s*Interest|Late Fees|Termination|Limitation of Liability|Service Levels\s*\(SLA\)|Audit)\b\s*[:\-/]*\s*",
        "",
        c,
        flags=re.IGNORECASE,
    )
    return c.strip()


def _clause_matches_topic(clause: str, topic: str) -> bool:
    c = (clause or "").lower()
    # Never map liability language into other headings.
    if topic != "liability" and any(k in c for k in ["liability", "limitation of liability", "capped", "uncapped", "cap at"]):
        return False

    if topic == "privacy":
        # Topic filter rule: include ONLY privacy/data protection/customer data.
        return any(k in c for k in ["privacy", "data protection", "personal data", "customer data"])

    if topic == "availability":
        # Service Availability filter: include only availability/uptime/maintenance statements.
        # STRICT RULES:
        # - Must match INCLUDE keywords
        # - Must be discarded if it contains any EXCLUDE keywords
        include = ["service availability", "availability", "uptime", "% of the time", "scheduled maintenance"]
        exclude = ["payment", "late", "interest", "invoice", "termination", "liability", "compliance"]

        if any(k in c for k in exclude):
            return False
        if not any(k in c for k in include) and "%" not in c:
            return False

        # Don't treat remedies as availability commitments.
        if "service credit" in c or "service credits" in c:
            return False

        return True

    if topic == "payment":
        # Payment Terms: timing + invoice obligations only.
        has_invoice = "invoice" in c or "invoic" in c
        has_due_timing = bool(re.search(r"\bwithin\b.*\bdays\b", c)) or "due" in c
        has_pay = "pay" in c or "payment" in c
        # Exclude late-fee language to keep headings clean.
        has_late = any(k in c for k in ["late", "interest", "penalt", "per month"])
        return (has_pay and (has_invoice or has_due_timing)) and not has_late
    if topic == "late":
        # Late Fees: interest/penalties/late charges only.
        has_late = any(k in c for k in ["late", "overdue", "delinquent"])
        has_charge = any(k in c for k in ["interest", "%", "per month", "penalt", "charge"])
        # Exclude core payment due-date language unless it is clearly about late charges.
        has_invoice_due = any(k in c for k in ["invoice", "within", "due", "undisputed"])
        return (has_charge and (has_late or "interest" in c)) and not (has_invoice_due and not has_late)
    if topic == "termination":
        # Termination questions: include only clauses about termination/breach/cure.
        # Avoid matching unrelated clauses that mention generic "notice" (e.g., audits).
        core = any(k in c for k in ["terminate", "termination", "breach", "cure"])
        return core
    if topic == "liability":
        return any(k in c for k in ["liability", "cap", "capped", "uncapped", "limitation"])
    if topic == "sla":
        return any(k in c for k in ["sla", "uptime", "service credit", "service credits"])
    if topic == "audit":
        return "audit" in c
    return False


def build_sanitized_answer(question: str, matches: List[RetrievalMatch]) -> Dict[str, Any]:
    """Answer sanitization:
    - Only clauses that directly answer the question
    - Exclude unrelated sections even if in the same chunk
    - Bullets are separate (no paragraph concatenation)
    """

    q = (question or "").strip()
    if not q or not matches:
        return {"question": q, "sections": []}

    topics = _requested_topics(q)
    keywords = _question_keywords(q)

    # Topic filter rule: if question is about privacy/data protection, restrict to privacy only.
    if "privacy" in topics:
        topics = ["privacy"]

    # Service availability filter: restrict to availability only.
    if "availability" in topics:
        topics = ["availability"]

    # Termination-specific filter: only include termination clauses.
    if "termination" in topics:
        topics = ["termination"]

    top_texts = [m.text for m in matches[:3] if (m.text or "").strip()]
    blob = "\n".join(top_texts)
    candidates: List[str] = []
    for raw in _split_into_clause_candidates(blob):
        norm = _normalize_clause(raw)
        if not norm:
            continue
        # Break combined clauses into atomic statements.
        for stmt in _split_into_atomic_statements(norm):
            s = _normalize_clause(stmt)
            if s:
                candidates.append(s)

    if not topics:
        # If user didn't name a clause family, we still require keyword match.
        topics = ["answer"]

    sections: List[Dict[str, Any]] = []
    seen: set[str] = set()

    def add_unique(bullets: List[str], text: str) -> None:
        t = " ".join((text or "").split()).strip()
        if not t:
            return
        k = t.lower()
        if k in seen:
            return
        seen.add(k)
        bullets.append(t[:260])

    for topic in topics:
        heading = _heading_for_fact_summary(q) if topic == "answer" else _topic_heading(topic)
        bullets: List[str] = []

        for c in candidates:
            cl = c.lower()
            if topic != "answer" and not _clause_matches_topic(c, topic):
                continue
            # For explicit headings (e.g., Payment Terms / Late Fees), semantic classifier
            # is the source of truth; keyword gating can cause false negatives (pay vs payment).
            if topic == "answer" and keywords and not any(k in cl for k in keywords):
                continue
            add_unique(bullets, c)
            if len(bullets) >= 3:
                break

        if bullets:
            sections.append({"heading": heading, "bullets": bullets})

    return {"question": q, "sections": sections}


def build_question_answer(question: str, matches: List[RetrievalMatch]) -> Dict[str, Any]:
    """Backwards compatible answer helper.

    Produces:
    - `sections`: structured sanitized answer
    - `answer`: human-readable string with headings + • bullets
    """

    sa = build_sanitized_answer(question, matches)
    sections = sa.get("sections") or []
    lines: List[str] = []
    for sec in sections:
        heading = (sec.get("heading") or "").strip()
        if heading:
            lines.append(heading)
        for b in sec.get("bullets") or []:
            lines.append(f"• {b}")
        lines.append("")

    answer = "\n".join(lines).strip()
    return {"question": sa.get("question") or (question or ""), "answer": answer, "sections": sections}


def _evidence_snippets(matches: List[RetrievalMatch], *, max_items: int = 5) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()
    for m in matches:
        if len(out) >= max_items:
            break
        snippet = " ".join(m.text.split())
        snippet = snippet[:240]
        key = snippet.lower()
        if not snippet or key in seen:
            continue
        seen.add(key)
        out.append(snippet)
    return out


def _agent_plan(agent_type: str, user_question: str) -> List[str]:
    base = (user_question or "").strip()
    if not base:
        return []

    if agent_type == "legal":
        return [
            base,
            f"termination breach {base}",
            f"indemnification liability {base}",
            "confidentiality NDA",
        ]
    if agent_type == "compliance":
        return [
            base,
            f"privacy data protection {base}",
            "audit reporting",
            "security incident breach notification",
        ]
    if agent_type == "finance":
        return [
            base,
            "payment terms fees invoices billing",
            "late fees interest penalties",
            "limitation of liability indemnification",
        ]
    if agent_type == "operations":
        return [
            base,
            "deliverables milestones timelines",
            "SLA uptime service credits",
            "performance standards support",
        ]

    return [base]


def run_agent(
    *,
    agent_type: str,
    question: str,
    rag: LocalRAGIndex,
    top_k_per_query: int = 5,
) -> Dict[str, Any]:
    queries = _agent_plan(agent_type, question)
    per_query: List[Dict[str, Any]] = []
    all_matches: List[RetrievalMatch] = []

    for q in queries:
        ms = rag.query(q, top_k=top_k_per_query)
        per_query.append(
            {
                "query": q,
                "matches": [
                    {"score": m.score, "chunk_index": m.chunk_index, "text": m.text[:500]} for m in ms
                ],
            }
        )
        all_matches.extend(ms)

    conf = confidence_from_matches(all_matches)
    combined_text = " ".join([m.text for m in all_matches])
    risk = infer_risk_from_text(combined_text)

    findings: List[str] = []
    if agent_type == "legal":
        findings = [
            "Review termination and breach triggers.",
            "Check indemnity and limitation of liability language.",
            "Confirm confidentiality / IP sections if present.",
        ]
    elif agent_type == "compliance":
        findings = [
            "Review privacy and data protection obligations.",
            "Check audit/reporting rights and breach notification clauses.",
            "Verify data retention/deletion requirements if present.",
        ]
    elif agent_type == "finance":
        findings = [
            "Review payment terms, invoicing, and due dates.",
            "Check late fees, penalties, and interest provisions.",
            "Confirm liability allocation and indemnity impacts.",
        ]
    elif agent_type == "operations":
        findings = [
            "Review deliverables, timelines, and acceptance criteria.",
            "Check SLA/uplink uptime commitments and service credits.",
            "Confirm support and escalation requirements.",
        ]

    return {
        "agent_type": agent_type,
        "question": question,
        "timestamp": utc_now_iso(),
        "confidence": conf,
        "risk_level": risk,
        "retrieval": {
            "top_k_per_query": top_k_per_query,
            "per_query": per_query,
        },
        "evidence": _evidence_snippets(all_matches, max_items=5),
        "findings": findings,
    }


def overall_risk(per_agent: Dict[str, str]) -> str:
    best = "low"
    for rl in per_agent.values():
        r = (rl or "unknown").lower()
        if RISK_ORDER.get(r, 1) > RISK_ORDER.get(best, 0):
            best = r
    if best not in {"low", "medium", "high"}:
        best = "medium"
    return best


TONE_TEMPLATES: Dict[str, Dict[str, str]] = {
    "executive": {
        "risk_prefix_high": "HIGH RISK",
        "risk_prefix_medium": "ELEVATED RISK",
        "risk_prefix_low": "LOW RISK",
        "phrase_review": "Prioritize review of the highlighted items.",
        "phrase_escalate": "Route to approval if risk is high.",
        "phrase_negotiate": "Negotiate risk-heavy terms where possible.",
        "evidence_label": "Key evidence",
    },
    "simple": {
        "risk_prefix_high": "HIGH RISK",
        "risk_prefix_medium": "MEDIUM RISK",
        "risk_prefix_low": "LOW RISK",
        "phrase_review": "Please review the highlighted clauses.",
        "phrase_escalate": "Get approval if the risk is high.",
        "phrase_negotiate": "Try to negotiate the risky terms.",
        "evidence_label": "Evidence",
    },
}


def _tone(name: str) -> Dict[str, str]:
    t = (name or "executive").strip().lower()
    return TONE_TEMPLATES.get(t, TONE_TEMPLATES["executive"])


def _risk_tag(risk_level: str, tone_name: str) -> str:
    t = _tone(tone_name)
    rl = (risk_level or "medium").strip().lower()
    if rl == "high":
        return t["risk_prefix_high"]
    if rl == "low":
        return t["risk_prefix_low"]
    return t["risk_prefix_medium"]


def _risk_rank(level: str) -> int:
    lv = (level or "").strip().lower()
    if lv == "high":
        return 3
    if lv == "medium":
        return 2
    if lv == "low":
        return 1
    return 0


def _max_risk(levels: List[str]) -> str:
    best = "unknown"
    best_rank = -1
    for lv in levels:
        r = _risk_rank(lv)
        if r > best_rank:
            best_rank = r
            best = (lv or "unknown").lower()
    if best not in {"low", "medium", "high"}:
        return "unknown"
    return best


def _clause_matches_compliance(clause: str) -> bool:
    c = (clause or "").lower()
    return any(
        k in c
        for k in [
            "privacy",
            "data protection",
            "personal data",
            "gdpr",
            "hipaa",
            "security",
            "incident",
            "breach",
            "notification",
            "retention",
            "subprocessor",
            "audit",
            "soc 2",
            "soc2",
            "iso 27001",
            "iso27001",
        ]
    )


def _extract_topic_statements(rag: LocalRAGIndex, *, query: str, topic: str, max_items: int = 5) -> List[str]:
    matches = rag.query(query, top_k=6)
    out: List[str] = []
    seen: set[str] = set()

    for m in matches:
        for raw in _split_into_clause_candidates(m.text):
            norm = _normalize_clause(raw)
            if not norm:
                continue
            for stmt in _split_into_atomic_statements(norm):
                s = _normalize_clause(stmt)
                if not s:
                    continue

                if topic == "compliance":
                    ok = _clause_matches_compliance(s)
                else:
                    ok = _clause_matches_topic(s, topic)

                if not ok:
                    continue
                k = s.lower()
                if k in seen:
                    continue
                seen.add(k)
                out.append(s[:320])
                if len(out) >= max_items:
                    return out

    return out


def _finance_risk(payment_terms: List[str], late_fees: List[str]) -> Tuple[str, List[str], List[Tuple[str, str]]]:
    """Return (risk_level, points, evidence_items(label,text))."""

    points: List[str] = []
    evidence: List[Tuple[str, str]] = []
    risks: List[str] = []

    # Payment terms risk
    pay_risk = "low"
    pay_clause = payment_terms[0] if payment_terms else ""
    if pay_clause:
        days = None
        m = re.search(r"\bwithin\s+(\d{1,3})\s*\(?\d*\)?\s+days\b", pay_clause.lower())
        if m:
            try:
                days = int(m.group(1))
            except Exception:
                days = None

        if "upon receipt" in pay_clause.lower() or "immediately" in pay_clause.lower():
            pay_risk = "high"
        elif days is not None and days <= 15:
            pay_risk = "medium"
        elif days is not None and days <= 30:
            pay_risk = "low"

        if days is not None:
            points.append(f"Payment Terms require payment within {days} days of invoice date.")
        else:
            points.append("Payment Terms specify a payment timing obligation tied to invoicing.")
        evidence.append(("Payment Terms", pay_clause))
        risks.append(pay_risk)

    # Late fees risk
    late_risk = "low"
    late_clause = late_fees[0] if late_fees else ""
    if late_clause:
        ml = late_clause.lower()
        pct = None
        mm = re.search(r"(\d+(?:\.\d+)?)\s*%.*\b(per month|monthly)\b", ml)
        if mm:
            try:
                pct = float(mm.group(1))
            except Exception:
                pct = None

        if any(k in ml for k in ["liquidated damages", "penalty", "punitive"]):
            late_risk = "high"
        elif pct is not None and pct >= 2.0:
            late_risk = "high"
        elif pct is not None and pct >= 1.0:
            late_risk = "medium"
        elif "interest" in ml and any(k in ml for k in ["per month", "monthly", "%"]):
            late_risk = "medium"

        if pct is not None:
            points.append(f"Late Fees accrue interest at {pct}% per month (as written in the late-fee clause).")
        else:
            points.append("Late Fees include an interest/charge provision for overdue amounts.")
        evidence.append(("Late Fees", late_clause))
        risks.append(late_risk)

    if not risks:
        return "n/a", ["No relevant clause identified for payment terms or late fees in the provided text."], []

    return _max_risk(risks), points, evidence


def _legal_risk(termination: List[str], liability: List[str]) -> Tuple[str, List[str], List[Tuple[str, str]]]:
    points: List[str] = []
    evidence: List[Tuple[str, str]] = []
    risks: List[str] = []

    term_risk = "low"
    term_clause = termination[0] if termination else ""
    if term_clause:
        days = None
        ml = term_clause.lower()
        m = re.search(r"\bwithin\s+(\d{1,3})\s*\(?\d*\)?\s+days\b", ml)
        if m:
            try:
                days = int(m.group(1))
            except Exception:
                days = None

        if "immediately" in ml or "without notice" in ml:
            term_risk = "high"
        elif days is not None and days < 10:
            term_risk = "high"
        elif days is not None and days < 30:
            term_risk = "medium"
        else:
            term_risk = "low"

        if days is not None:
            points.append(f"Termination for material breach requires a {days}-day cure period after written notice.")
        else:
            points.append("Termination for material breach includes a cure/notice framework in the termination clause.")
        evidence.append(("Termination", term_clause))
        risks.append(term_risk)

    liab_risk = "low"
    liab_clause = liability[0] if liability else ""
    if liab_clause:
        ml = liab_clause.lower()
        if any(k in ml for k in ["uncapped", "unlimited"]):
            # Only mark HIGH when uncapped is broad. If the contract is generally capped
            # with a specific uncapped exception (common for confidentiality), treat as MEDIUM.
            if ("except" in ml or "excluding" in ml) and any(k in ml for k in ["cap", "capped", "fees paid"]):
                liab_risk = "medium"
            else:
                liab_risk = "high"
        elif any(k in ml for k in ["capped", "cap", "fees paid"]):
            liab_risk = "medium"
        else:
            liab_risk = "medium"

        if "capped" in ml or "cap" in ml or "fees paid" in ml:
            points.append("Limitation of Liability caps aggregate liability based on fees paid (with stated exceptions, if any).")
        else:
            points.append("Limitation of Liability defines liability allocation and any cap/exception structure.")
        evidence.append(("Limitation of Liability", liab_clause))
        risks.append(liab_risk)

    if not risks:
        return "n/a", ["No relevant clause identified for termination or limitation of liability in the provided text."], []

    return _max_risk(risks), points, evidence


def _operations_risk(availability: List[str], sla: List[str]) -> Tuple[str, List[str], List[Tuple[str, str]]]:
    """Operations risk derived from availability/SLA clauses.

    If service availability text exists, this section must not be N/A.
    """

    clause = (availability[0] if availability else "") or (sla[0] if sla else "")
    if not clause:
        return "n/a", ["No relevant clause identified for service availability / service levels (SLA) in the provided text."], []

    ml = clause.lower()
    risk = "low"
    m = re.search(r"\b(\d{2}\.\d+)\s*%\b", ml)
    if m:
        try:
            pct = float(m.group(1))
            if pct < 99.0:
                risk = "medium"
        except Exception:
            pass
    pts: List[str] = []
    m2 = re.search(r"\b(\d{2}\.\d+)\s*%\b", ml)
    if m2:
        pts.append(f"SLA includes an uptime commitment of {m2.group(1)}%.")
    if "availability" in ml or "service availability" in ml:
        pts.append("The agreement states a service availability / uptime commitment.")
    if "scheduled maintenance" in ml:
        pts.append("The availability commitment references scheduled maintenance exclusions.")
    if "service credit" in ml:
        pts.append("SLA includes service credits as the stated remedy if uptime is not met.")
    if not pts:
        pts = ["SLA/service levels are defined in the provided text."]
    evidence_label = "Service Availability" if (availability and clause == availability[0]) else "Service Levels (SLA)"
    evidence = [(evidence_label, clause)]
    return risk, pts, evidence


def _compliance_risk(compliance: List[str]) -> Tuple[str, List[str], List[Tuple[str, str]]]:
    if not compliance:
        # Assign no risk if no relevant clauses exist.
        return "n/a", ["No relevant clause identified for privacy/data protection, breach notification, retention, or audit/security controls in the provided text."], []

    clause = compliance[0]
    ml = clause.lower()
    risk = "low"
    if any(k in ml for k in ["immediately", "24 hours", "within 24"]):
        risk = "medium"

    points: List[str] = []
    if "audit" in ml:
        points.append("The contract grants audit rights related to security controls.")
    if "security" in ml:
        points.append("The contract references security controls in the compliance-related language.")

    # Explicitly state missing privacy/breach families without speculating beyond the provided text.
    blob = " ".join([c.lower() for c in compliance])
    if not any(k in blob for k in ["privacy", "data protection", "personal data", "gdpr", "hipaa"]):
        points.append("No explicit privacy/data protection obligations were identified in the provided text.")
    if not any(k in blob for k in ["breach", "incident", "notification"]):
        points.append("No explicit breach notification/incident reporting obligations were identified in the provided text.")

    if not points:
        points = ["Compliance-related language is present in the provided text."]

    evidence = [("Compliance", clause)]
    return risk, points, evidence


def build_executive_report_data(
    *,
    contract_text: str,
    rag: LocalRAGIndex,
    question: Optional[str] = None,
    selected_agents: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build contract-specific executive risk analysis backed by explicit clause evidence.

    If a question is specific (e.g., about payment terms), only the relevant agent sections
    are generated to avoid unrelated content in the executive report.
    """

    all_agents = ["legal", "compliance", "finance", "operations"]
    if selected_agents is None:
        selected_agents = select_agents_for_question(question) if (question or "").strip() else all_agents

    selected_set = set([a for a in (selected_agents or []) if a in set(all_agents)])
    # If something goes wrong with selection, default to all.
    if not selected_set:
        selected_set = set(all_agents)

    def _skipped_section() -> Tuple[str, List[str], List[Tuple[str, str]]]:
        return "n/a", ["Skipped (not relevant to the question)."], []

    payment_terms: List[str] = []
    late_fees: List[str] = []
    termination: List[str] = []
    liability: List[str] = []
    availability: List[str] = []
    sla: List[str] = []
    compliance: List[str] = []

    if "finance" in selected_set:
        payment_terms = _extract_topic_statements(
            rag,
            query="payment terms invoice due within days undisputed amounts",
            topic="payment",
            max_items=3,
        )
        late_fees = _extract_topic_statements(
            rag,
            query="late fees interest overdue per month penalty",
            topic="late",
            max_items=3,
        )

    if "legal" in selected_set:
        termination = _extract_topic_statements(
            rag,
            query="termination terminate material breach cure notice",
            topic="termination",
            max_items=3,
        )
        liability = _extract_topic_statements(
            rag,
            query="limitation of liability liability cap capped uncapped",
            topic="liability",
            max_items=2,
        )

    if "operations" in selected_set:
        availability = _extract_topic_statements(
            rag,
            query="service availability availability uptime % of the time scheduled maintenance",
            topic="availability",
            max_items=2,
        )
        sla = _extract_topic_statements(
            rag,
            query="SLA uptime service credits service level",
            topic="sla",
            max_items=2,
        )

    if "compliance" in selected_set:
        compliance = _extract_topic_statements(
            rag,
            query="privacy data protection security breach notification incident retention subprocessor audit",
            topic="compliance",
            max_items=3,
        )

    if "finance" in selected_set:
        finance_risk, finance_points, finance_ev = _finance_risk(payment_terms, late_fees)
    else:
        finance_risk, finance_points, finance_ev = _skipped_section()

    if "legal" in selected_set:
        legal_risk, legal_points, legal_ev = _legal_risk(termination, liability)
    else:
        legal_risk, legal_points, legal_ev = _skipped_section()

    if "operations" in selected_set:
        ops_risk, ops_points, ops_ev = _operations_risk(availability, sla)
    else:
        ops_risk, ops_points, ops_ev = _skipped_section()

    if "compliance" in selected_set:
        comp_risk, comp_points, comp_ev = _compliance_risk(compliance)
    else:
        comp_risk, comp_points, comp_ev = _skipped_section()

    overall_candidates = [r for r in [finance_risk, legal_risk, ops_risk, comp_risk] if (r or "").lower() in {"low", "medium", "high"}]
    overall = _max_risk(overall_candidates) if overall_candidates else "unknown"

    # Executive Summary: 2–3 high-level conclusions explaining WHY overall risk.
    summary_candidates: List[Tuple[int, str]] = []
    if ("finance" in selected_set) and finance_risk in {"low", "medium", "high"} and (payment_terms or late_fees):
        summary_candidates.append(
            (
                _risk_rank(finance_risk),
                f"Finance risk is {finance_risk.upper()} based on the payment timing and late-fee structure stated in the agreement.",
            )
        )
    if ("legal" in selected_set) and legal_risk in {"low", "medium", "high"} and (termination or liability):
        summary_candidates.append(
            (
                _risk_rank(legal_risk),
                f"Legal risk is {legal_risk.upper()} based on the termination-for-breach framework and the liability allocation/cap structure.",
            )
        )
    if ("operations" in selected_set) and ops_risk in {"low", "medium", "high"} and sla:
        summary_candidates.append(
            (
                _risk_rank(ops_risk),
                f"Operations risk is {ops_risk.upper()} based on the defined SLA commitments and stated remedies (e.g., service credits).",
            )
        )
    if ("compliance" in selected_set) and comp_risk in {"low", "medium", "high"} and compliance:
        summary_candidates.append(
            (
                _risk_rank(comp_risk),
                f"Compliance risk is {comp_risk.upper()} based on compliance-related language present in the provided text.",
            )
        )

    # Prefer higher-risk takeaways first.
    summary_candidates.sort(key=lambda x: (-x[0], len(x[1])))
    summary_points = [t for _, t in summary_candidates[:3]]
    if not summary_points:
        summary_points = ["No relevant risk-bearing clauses were identified in the provided text for the reviewed categories."]
        overall = "unknown"

    # Build Key Evidence list using only items referenced in section evidence.
    key_evidence: List[Tuple[str, str]] = []
    for label, txt in (finance_ev + legal_ev + ops_ev + comp_ev):
        key_evidence.append((label, txt))

    analysis = {
        "legal": {
            "risk_level": legal_risk,
            "findings": legal_points,
            "evidence": [t for _, t in legal_ev],
        },
        "compliance": {
            "risk_level": comp_risk,
            "findings": comp_points,
            "evidence": [t for _, t in comp_ev],
        },
        "finance": {
            "risk_level": finance_risk,
            "findings": finance_points,
            "evidence": [t for _, t in finance_ev],
        },
        "operations": {
            "risk_level": ops_risk,
            "findings": ops_points,
            "evidence": [t for _, t in ops_ev],
        },
        "overall_risk": overall,
        "executive_summary_points": summary_points[:3],
        "key_evidence": [{"label": lab, "text": txt} for lab, txt in key_evidence],
    }

    return analysis


def _sanitize_evidence_text(text: str) -> Optional[str]:
    """Evidence sanitization.

    Rules:
    - Trim broken/partial sentences where possible
    - Discard evidence shorter than 10 characters
    - Discard evidence starting with non-alphabetic characters
    """

    t = " ".join((text or "").split()).strip()
    if len(t) < 10:
        return None
    if not re.match(r"^[A-Za-z]", t):
        return None

    # Prefer complete sentence boundaries.
    parts = [p.strip() for p in re.split(r"(?<=[\.!?])\s+", t) if p.strip()]
    cleaned = " ".join(parts).strip() if parts else t
    if len(cleaned) < 10:
        return None
    return cleaned


def format_report(final_json: Dict[str, Any], *, tone: str = "executive") -> str:
    """Final Executive Contract Analysis Report.

    Rules:
    - Do NOT repeat the user's question.
    - No generic filler statements.
    - Risk levels must be justified by actual contract language.
    - Sections are N/A when relevant clauses are absent.
    """

    analysis = final_json.get("analysis") or {}
    overall = (analysis.get("overall_risk") or "unknown").upper()
    summary_points = analysis.get("executive_summary_points") or []

    def fmt_level(lv: str) -> str:
        x = (lv or "").strip().lower()
        if x in {"low", "medium", "high"}:
            return x.upper()
        return "N/A" if x == "n/a" else "UNKNOWN"

    lines: List[str] = []
    lines.append("CONTRACT ANALYSIS REPORT (Executive)")
    lines.append("")

    lines.append("Executive Summary")
    lines.append(f"- Overall contract risk: {overall}")
    for p in summary_points:
        if (p or "").strip():
            lines.append(f"- {p}")

    selected_agents = (final_json.get("agent_analysis") or {}).get("selected_agents")
    if isinstance(selected_agents, list) and selected_agents:
        sections = [s for s in selected_agents if s in {"legal", "compliance", "finance", "operations"}]
    else:
        sections = ["legal", "compliance", "finance", "operations"]

    for section in sections:
        sec = analysis.get(section) or {}
        lines.append("")
        lines.append(section.title())
        lines.append(f"Risk Level: {fmt_level(sec.get('risk_level') or 'n/a')}")
        findings = [f for f in (sec.get("findings") or []) if (f or "").strip()]
        if not findings:
            lines.append("- No relevant clause identified.")
        else:
            # Keep each section to max 2 bullet points.
            for f in findings[:2]:
                lines.append(f"- {f}")

    lines.append("")
    lines.append("Key Evidence")
    key_evidence = analysis.get("key_evidence") or []
    if not key_evidence:
        lines.append("- No supporting clause evidence extracted.")
    else:
        for item in key_evidence[:10]:
            lab = (item.get("label") or "Evidence").strip()
            txt = _sanitize_evidence_text(item.get("text") or "")
            if not txt:
                continue
            lines.append(f"- {lab}: {txt[:240]}")

    return "\n".join(lines).strip()


def _memory_path(contract_id: str) -> Path:
    return MEMORY_DIR / f"{contract_id}.json"


def _load_memory(contract_id: str) -> List[Dict[str, Any]]:
    p = _memory_path(contract_id)
    if not p.exists():
        return []
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save_memory(contract_id: str, records: List[Dict[str, Any]]) -> None:
    p = _memory_path(contract_id)
    p.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def _vec_to_list(v: np.ndarray) -> List[float]:
    return [float(x) for x in v.tolist()]


def _list_to_vec(v: Any) -> Optional[np.ndarray]:
    if not isinstance(v, list) or not v:
        return None
    try:
        return np.asarray(v, dtype=np.float32)
    except Exception:
        return None


def _top_sim(vec: np.ndarray, others: List[np.ndarray]) -> Optional[float]:
    if vec is None or not others:
        return None
    v = vec / (np.linalg.norm(vec) + 1e-12)
    sims = []
    for o in others:
        if getattr(o, "shape", None) != getattr(vec, "shape", None):
            continue
        on = o / (np.linalg.norm(o) + 1e-12)
        sims.append(float(np.dot(v, on)))
    return max(sims) if sims else None


async def run_full_pipeline(
    *,
    contract_text: str,
    question: str,
    tone: str = "executive",
    contract_id: Optional[str] = None,
    model_name: Optional[str] = None,
    no_evidence_threshold: float = 0.25,
    intent_override: Optional[str] = None,
    run_all_agents: bool = False,
) -> Tuple[Dict[str, Any], str]:
    """End-to-end pipeline.

    1) RAG retrieval (local embeddings)
    2) Parallel agents (async)
    3) Memory lookup/refinement (local disk)
    4) Final JSON
    5) Report formatting
    """
    if not (contract_text or "").strip():
        raise ValueError("Empty contract_text")
    if not (question or "").strip():
        raise ValueError("Empty question")

    contract_id = contract_id or stable_contract_id(contract_text)

    override = (intent_override or "").strip().lower()
    allowed = {"fact_summary", "clause_extraction", "qa", "risk_analysis", "executive_review"}
    intent = override if override in allowed else detect_intent(question)

    selected_agents_for_exec: Optional[List[str]] = None
    if intent in {"risk_analysis", "executive_review"}:
        if run_all_agents:
            selected_agents_for_exec = ["legal", "compliance", "finance", "operations"]
        else:
            selected_agents_for_exec = select_agents_for_question(question)

    model_name = model_name or os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    rag = LocalRAGIndex(model_name=model_name)
    rag.build(contract_text)

    # Evidence probe for safe grounding.
    probe = rag.query(question, top_k=3)
    best_score = max([m.score for m in probe], default=None)

    # For risk_analysis/executive_review, use clause-extraction evidence as the gate.
    # This avoids false negatives when the user's phrasing ("risk analysis") doesn't
    # appear in the contract text but relevant clauses do.
    executive_analysis: Optional[Dict[str, Any]] = None
    if intent in {"risk_analysis", "executive_review"}:
        executive_analysis = build_executive_report_data(
            contract_text=contract_text,
            rag=rag,
            question=question,
            selected_agents=selected_agents_for_exec,
        )
        has_exec_evidence = bool(executive_analysis.get("key_evidence"))
        no_evidence = not has_exec_evidence
    else:
        no_evidence = best_score is None or best_score < float(no_evidence_threshold)

    # Strict minimal output unless user explicitly asked for risk/review/analysis.
    if intent in {"fact_summary", "qa", "clause_extraction"}:
        qa = build_question_answer(question, probe)
        report = format_fact_summary_report(question, probe)
        # Populate minimal analysis object so frontend can find evidence for highlighting
        final_json = {
            "contract_id": contract_id,
            "generated_at": utc_now_iso(),
            "intent": intent,
            "question": question,
            "qa": qa,
            "analysis": {
                "key_evidence": [{"text": m.text, "score": m.score} for m in probe]
            },
            "confidence": None,
            "high_risk_evidence": [],
            "no_evidence": bool(no_evidence),
            "evidence_score": best_score,
            "message": "No relevant evidence found in the provided document for this question." if no_evidence else None,
        }
        return final_json, report

    # For risk_analysis/executive_review, still avoid hallucinations.
    if no_evidence:
        qa = build_question_answer(question, probe)
        if executive_analysis is None:
            executive_analysis = {
                "legal": {"risk_level": "unknown", "findings": [], "evidence": []},
                "compliance": {"risk_level": "unknown", "findings": [], "evidence": []},
                "finance": {"risk_level": "unknown", "findings": [], "evidence": []},
                "operations": {"risk_level": "unknown", "findings": [], "evidence": []},
                "overall_risk": "unknown",
                "executive_summary_points": [
                    "No relevant supporting contract language was retrieved for the requested analysis.",
                ],
                "key_evidence": [],
            }
        final_json = {
            "contract_id": contract_id,
            "generated_at": utc_now_iso(),
            "intent": intent,
            "question": question,
            "qa": qa,
            "analysis": executive_analysis,
            "agent_analysis": {
                "selected_agents": selected_agents_for_exec
                or (["legal", "compliance", "finance", "operations"] if run_all_agents else select_agents_for_question(question)),
            },
            "confidence": {"overall_avg": None, "per_agent": {}},
            "high_risk_evidence": [],
            "no_evidence": True,
            "evidence_score": best_score,
            "message": "No relevant evidence found in the provided document for this question.",
        }
        report = format_report(final_json, tone=tone)
        return final_json, report

    mem = _load_memory(contract_id)
    q_vec_np = rag.encode([question], normalize_embeddings=True)[0]

    selected_agents = selected_agents_for_exec or select_agents_for_question(question)
    tasks: List[asyncio.Future] = []
    task_types: List[str] = []
    for agent_type in selected_agents:
        tasks.append(asyncio.to_thread(run_agent, agent_type=agent_type, question=question, rag=rag))
        task_types.append(agent_type)

    results: List[Dict[str, Any]] = []
    if tasks:
        results = await asyncio.gather(*tasks)

    agent_map: Dict[str, Dict[str, Any]] = {t: r for t, r in zip(task_types, results)}

    def _skipped(agent_type: str) -> Dict[str, Any]:
        return {
            "agent_type": agent_type,
            "question": question,
            "timestamp": utc_now_iso(),
            "confidence": None,
            "risk_level": "n/a",
            "retrieval": {"top_k_per_query": 0, "per_query": []},
            "evidence": [],
            "findings": [],
            "skipped": True,
        }

    legal = agent_map.get("legal") or _skipped("legal")
    compliance = agent_map.get("compliance") or _skipped("compliance")
    finance = agent_map.get("finance") or _skipped("finance")
    operations = agent_map.get("operations") or _skipped("operations")

    per_agent_risk = {
        "legal": (legal or {}).get("risk_level"),
        "compliance": (compliance or {}).get("risk_level"),
        "finance": (finance or {}).get("risk_level"),
        "operations": (operations or {}).get("risk_level"),
    }
    per_agent_conf = {
        "legal": (legal or {}).get("confidence"),
        "compliance": (compliance or {}).get("confidence"),
        "finance": (finance or {}).get("confidence"),
        "operations": (operations or {}).get("confidence"),
    }
    conf_vals = [v for v in per_agent_conf.values() if isinstance(v, (int, float))]
    overall_conf = (sum(conf_vals) / len(conf_vals)) if conf_vals else None

    evidence_pool: List[str] = []
    for sec in [legal, compliance, finance, operations]:
        for ev in (sec or {}).get("evidence") or []:
            if any(t in (ev or "").lower() for t in HIGH_RISK_TERMS):
                evidence_pool.append(ev)

    # Deduplicate evidence while preserving order.
    deduped_evidence: List[str] = []
    seen_evidence: set[str] = set()
    for ev in evidence_pool:
        k = (ev or "").strip().lower()
        if not k or k in seen_evidence:
            continue
        seen_evidence.add(k)
        deduped_evidence.append(ev)

    final_json = {
        "contract_id": contract_id,
        "generated_at": utc_now_iso(),
        "intent": intent,
        "question": question,
        "qa": build_question_answer(question, probe),
        # Executive report analysis is generated from extracted clauses only (no filler).
        "analysis": executive_analysis
        or build_executive_report_data(
            contract_text=contract_text,
            rag=rag,
            question=question,
            selected_agents=selected_agents,
        ),
        # Keep agent outputs for debugging, but do not use them to format the executive report.
        "agent_analysis": {
            "selected_agents": selected_agents,
            "legal": legal,
            "compliance": compliance,
            "finance": finance,
            "operations": operations,
        },
        "confidence": {
            "overall_avg": overall_conf,
            "per_agent": per_agent_conf,
        },
        "high_risk_evidence": deduped_evidence[:12],
        "no_evidence": False,
        "evidence_score": best_score,
    }

    report = format_report(final_json, tone=tone)

    mem.append(
        {
            "type": "final",
            "timestamp": utc_now_iso(),
            "question": question,
            "question_embedding": _vec_to_list(q_vec_np),
            "final_json": final_json,
        }
    )
    _save_memory(contract_id, mem)

    return final_json, report
