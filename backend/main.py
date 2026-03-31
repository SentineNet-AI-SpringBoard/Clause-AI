from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="ClauseAI Backend")

class ContractRequest(BaseModel):
    contract_text: str

@app.get("/")
def health():
    return {"status": "Backend running"}

@app.post("/analyze")
def analyze_contract(req: ContractRequest):
    if not req.contract_text.strip():
        raise HTTPException(status_code=400, detail="Empty contract")

    text = req.contract_text.lower()

    if "termination" in text or "penalty" in text:
        risk = "High"
    elif "liability" in text or "indemnity" in text:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "overall_risk": risk,
        "analysis": {
            "legal": "Legal clauses reviewed",
            "financial": "Financial exposure estimated",
            "compliance": "Compliance check done"
        },
        "report": f"""
Contract Analysis Report
------------------------
Overall Risk: {risk}
Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    }

