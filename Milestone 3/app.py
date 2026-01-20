from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import io
import re

# ---- File parsers ----
from PyPDF2 import PdfReader
from docx import Document

# ---- Your pipeline ----
from pipeline.final_pipeline import run_full_analysis
from reporting.formatter import format_full_report, generate_executive_summary

# =====================================================
# APP INIT
# =====================================================

app = FastAPI(title="ClauseAI Contract Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# HELPERS
# =====================================================

def extract_text(file: UploadFile) -> str:
    ext = file.filename.split(".")[-1].lower()

    if ext == "txt":
        return file.file.read().decode("utf-8", errors="ignore")

    elif ext == "pdf":
        reader = PdfReader(file.file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    elif ext == "docx":
        doc = Document(io.BytesIO(file.file.read()))
        return "\n".join(p.text for p in doc.paragraphs)

    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")


def validate_contract_text(text: str) -> str:
    if len(text.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Contract text must be at least 20 characters"
        )
    return text.strip()


def extract_relevant_sentences(
    text: str,
    question: str,
    limit: int = 6
) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)

    keywords = {
        word.lower()
        for word in re.findall(r'\w+', question)
        if len(word) > 3
    }

    matches = []
    for sentence in sentences:
        s_lower = sentence.lower()
        if any(k in s_lower for k in keywords):
            matches.append(sentence.strip())

    return matches[:limit]


# =====================================================
# ANALYSIS ENDPOINT (FILE UPLOAD)
# =====================================================

@app.post("/analyze")
async def analyze_contract(
    file: UploadFile = File(...),
    tone: str = Form("executive")
):
    text = extract_text(file)
    contract_text = validate_contract_text(text)

    final_output = run_full_analysis(contract_text)

    tone = tone.lower()
    if tone == "executive":
        report = generate_executive_summary(final_output)
    else:
        report = format_full_report(final_output, tone=tone)

    return {
        "contract_id": final_output["contract_id"],
        "overall_risk": final_output["overall_risk"],
        "tone": tone,
        "report": report,
        "analysis": final_output
    }


# =====================================================
# CHAT / QUESTION ANSWERING (DOCUMENT-GROUNDED)
# =====================================================

class QuestionRequest(BaseModel):
    contract_text: str
    question: str


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    contract_text = validate_contract_text(request.contract_text)

    matches = extract_relevant_sentences(
        contract_text,
        request.question
    )

    if not matches:
        return {
            "answer": "❌ No relevant information found in the uploaded document."
        }

    answer = "### 📄 Relevant excerpts from the document:\n\n"
    for i, sentence in enumerate(matches, 1):
        answer += f"{i}. {sentence}\n\n"

    return {
        "answer": answer
    }


# =====================================================
# HEALTH & ROOT
# =====================================================

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {
        "message": "ClauseAI API running",
        "status": "ok"
    }
