from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

from pipeline.final_pipeline import run_full_analysis
from reporting.formatter import format_full_report, generate_executive_summary

app = FastAPI(title="ClauseAI Contract Analysis API")

# =====================================================
# Request Models
# =====================================================

class AnalysisRequest(BaseModel):
    contract_text: str
    tone: str = "executive"          # executive | simple | formal
    include_report: bool = True


class QuickAnalysisRequest(BaseModel):
    contract_text: str


# =====================================================
# Helpers
# =====================================================

def validate_contract_text(text: str):
    if len(text.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Contract text must be at least 20 characters."
        )
    return text.strip()


# =====================================================
# Main Analysis Endpoint (FULL PIPELINE)
# =====================================================

@app.post("/analyze")
async def analyze_contract(request: AnalysisRequest):

    contract_text = validate_contract_text(request.contract_text)

    # Run full analysis pipeline
    final_output = run_full_analysis(contract_text)

    tone = request.tone.lower()
    if tone not in ["executive", "simple", "formal"]:
        raise HTTPException(
            status_code=400,
            detail="Tone must be one of: executive, simple, formal."
        )

    # Generate report (optional)
    if request.include_report:
        if tone == "executive":
            report = generate_executive_summary(final_output)
        else:
            report = format_full_report(final_output, tone=tone)
    else:
        report = None

    return {
        "contract_id": final_output["contract_id"],
        "overall_risk": final_output["overall_risk"],
        "tone": tone,
        "report": report
    }


# =====================================================
# QUICK ANALYSIS ENDPOINT (TC009 FIX)
# =====================================================

@app.post("/analyze/quick")
async def quick_analyze(request: QuickAnalysisRequest):

    contract_text = validate_contract_text(request.contract_text)

    final_output = run_full_analysis(contract_text)

    return {
        "contract_id": final_output["contract_id"],
        "overall_risk": final_output["overall_risk"]
    }


# =====================================================
# Health Check
# =====================================================

@app.get("/health")
def health_check():
    return {
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat()
    }


# =====================================================
# Root Endpoint
# =====================================================

@app.get("/")
def root():
    return {
        "status": "API running",
        "message": "Welcome to ClauseAI"
    }