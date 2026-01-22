from __future__ import annotations

import io
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from contract_pipeline import run_full_pipeline, stable_contract_id
from db_sqlite import (
    create_user,
    delete_analysis_run,
    get_analysis_run,
    init_db,
    list_analysis_runs,
    login,
    save_analysis_run,
    seed_demo_users,
    user_from_token,
)


app = FastAPI(title="Contract Analysis API (Milestone 3)", version="1.0")

# CORS for browser-based UIs (Milestone 4).
# Configure with env var FRONTEND_ORIGINS="http://localhost:5173,http://localhost:3000"
_origins_env = os.getenv("FRONTEND_ORIGINS", "").strip()
if _origins_env:
    allowed_origins = [o.strip() for o in _origins_env.split(",") if o.strip()]
else:
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _bearer_token(auth_header: str | None) -> str | None:
    if not auth_header:
        return None
    value = auth_header.strip()
    if not value:
        return None
    if value.lower().startswith("bearer "):
        return value.split(" ", 1)[1].strip() or None
    return value


def _require_user(authorization: str | None) -> dict:
    token = _bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Missing Authorization")
    user = user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user


class AnalyzeTextRequest(BaseModel):
    contract_text: str = Field(..., description="Extracted contract text")
    question: str = Field(..., description="User question")
    tone: str = Field("executive", description="executive | simple")
    no_evidence_threshold: float = Field(0.25, ge=0.0, le=1.0)
    contract_id: Optional[str] = None
    intent_override: Optional[str] = Field(
        None,
        description="Optional intent override: fact_summary | qa | clause_extraction | risk_analysis | executive_review",
    )
    run_all_agents: bool = Field(
        False,
        description="If true, force running all agents for Launch Analysis (executive report), regardless of query topic.",
    )


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "User"


class LoginRequest(BaseModel):
    email: str
    password: str


class HistorySaveRequest(BaseModel):
    mode: str
    question: str
    tone: str = "executive"
    run_all_agents: bool = False
    no_evidence_threshold: float = 0.62
    filenames: list[str] = []
    results: list[dict] = []


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _read_upload_text(upload: UploadFile) -> str:
    data = await upload.read()
    if not data:
        return ""

    name = (upload.filename or "").lower()
    content_type = (upload.content_type or "").lower()

    # Plain text
    if name.endswith(".txt") or content_type.startswith("text/"):
        return data.decode("utf-8", errors="ignore")

    # PDF
    if name.endswith(".pdf") or content_type == "application/pdf":
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(io.BytesIO(data))
            pages = []
            for p in reader.pages:
                pages.append(p.extract_text() or "")
            return "\n".join(pages)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not parse PDF: {e}")

    # DOCX
    if name.endswith(".docx"):
        try:
            import docx

            doc = docx.Document(io.BytesIO(data))
            return "\n".join([p.text for p in doc.paragraphs if p.text])
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not parse DOCX: {e}")

    # Fallback: treat as utf-8 text
    return data.decode("utf-8", errors="ignore")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "ts": _utc_now_iso()}


@app.on_event("startup")
def _startup():
    init_db()
    seed_demo_users()


@app.post("/auth/register")
def register(req: RegisterRequest):
    ok, msg = create_user(email=req.email, password=req.password, name=req.name, role=req.role)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"ok": True, "message": msg}


@app.post("/auth/login")
def auth_login(req: LoginRequest):
    res = login(email=req.email, password=req.password)
    if not res:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token, user = res
    return {"ok": True, "token": token, "user": user}


@app.get("/auth/me")
def auth_me(authorization: str | None = Header(default=None)):
    user = _require_user(authorization)
    return {"ok": True, "user": user}


@app.get("/history")
def history_list(limit: int = 10, authorization: str | None = Header(default=None)):
    user = _require_user(authorization)
    runs = list_analysis_runs(user_email=user["email"], limit=limit)
    return {"ok": True, "runs": runs}


@app.post("/history/save")
def history_save(req: HistorySaveRequest, authorization: str | None = Header(default=None)):
    user = _require_user(authorization)
    run_id = save_analysis_run(
        user_email=user["email"],
        mode=req.mode,
        question=req.question,
        tone=req.tone,
        run_all_agents=req.run_all_agents,
        no_evidence_threshold=req.no_evidence_threshold,
        filenames=req.filenames,
        results=req.results,
    )
    return {"ok": True, "id": run_id}


@app.get("/history/{run_id}")
def history_get(run_id: int, authorization: str | None = Header(default=None)):
    user = _require_user(authorization)
    run = get_analysis_run(user_email=user["email"], run_id=run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True, "run": run}


@app.delete("/history/{run_id}")
def history_delete(run_id: int, authorization: str | None = Header(default=None)):
    user = _require_user(authorization)
    ok = delete_analysis_run(user_email=user["email"], run_id=run_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


@app.post("/analyze")
async def analyze_contract(
    file: UploadFile = File(...),
    question: str = Form(...),
    tone: str = Form("executive"),
    no_evidence_threshold: float = Form(0.25),
    contract_id: Optional[str] = Form(None),
    intent_override: Optional[str] = Form(None),
    run_all_agents: bool = Form(False),
) -> dict:
    if not question or not question.strip():
        raise HTTPException(status_code=400, detail="Question is required")

    try:
        contract_text = await _read_upload_text(file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read upload: {e}")

    if not contract_text.strip():
        raise HTTPException(status_code=400, detail="Uploaded file is empty or could not be extracted")

    cid = contract_id.strip() if isinstance(contract_id, str) and contract_id.strip() else stable_contract_id(contract_text)

    try:
        final_json, report = await run_full_pipeline(
            contract_text=contract_text,
            question=question,
            tone=tone,
            contract_id=cid,
            no_evidence_threshold=float(no_evidence_threshold),
            intent_override=intent_override,
            run_all_agents=bool(run_all_agents),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    return {
        "contract_id": cid,
        "generated_at": final_json.get("generated_at"),
        "intent": final_json.get("intent"),
        "question": final_json.get("question"),
        "qa": final_json.get("qa"),
        "analysis": final_json.get("analysis"),
        "agent_analysis": final_json.get("agent_analysis"),
        "confidence": final_json.get("confidence"),
        "no_evidence": final_json.get("no_evidence"),
        "evidence_score": final_json.get("evidence_score"),
        "report": report,
    }


@app.post("/analyze_text")
async def analyze_contract_text(payload: AnalyzeTextRequest) -> dict:
    if not payload.question or not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question is required")
    if not payload.contract_text or not payload.contract_text.strip():
        raise HTTPException(status_code=400, detail="contract_text is empty")

    cid = (
        payload.contract_id.strip()
        if isinstance(payload.contract_id, str) and payload.contract_id.strip()
        else stable_contract_id(payload.contract_text)
    )

    try:
        final_json, report = await run_full_pipeline(
            contract_text=payload.contract_text,
            question=payload.question,
            tone=payload.tone,
            contract_id=cid,
            no_evidence_threshold=float(payload.no_evidence_threshold),
            intent_override=payload.intent_override,
            run_all_agents=bool(payload.run_all_agents),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {e}")

    return {
        "contract_id": cid,
        "generated_at": final_json.get("generated_at"),
        "intent": final_json.get("intent"),
        "question": final_json.get("question"),
        "qa": final_json.get("qa"),
        "analysis": final_json.get("analysis"),
        "agent_analysis": final_json.get("agent_analysis"),
        "confidence": final_json.get("confidence"),
        "no_evidence": final_json.get("no_evidence"),
        "evidence_score": final_json.get("evidence_score"),
        "report": report,
    }
