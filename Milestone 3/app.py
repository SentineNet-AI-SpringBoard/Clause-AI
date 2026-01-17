from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import os
import json
import sys
import hashlib
import traceback
import subprocess


try:
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    CURRENT_DIR = os.getcwd()

PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)


app = FastAPI(
    title="Contract Analysis API",
    description="Milestone 3 – Multi-Agent Cross-Refined Contract Risk Analysis",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if os.path.exists(os.path.join(PARENT_DIR, "Data", "Results", "Milestone3")):
    MILESTONE3_OUTPUT = os.path.join(PARENT_DIR, "Data", "Results", "Milestone3")
else:
    MILESTONE3_OUTPUT = "./output"

os.makedirs(MILESTONE3_OUTPUT, exist_ok=True)


class ContractAnalysisRequest(BaseModel):
    contract_text: str
    tone: Optional[str] = "executive"
    include_report: Optional[bool] = True

class AgentAssessment(BaseModel):
    agent_name: str
    risk_level: str
    confidence: float
    num_clauses: int
    is_refined: bool
    escalation_reasons: List[str]

class ContractAnalysisResponse(BaseModel):
    contract_id: str
    generated_at: str
    overall_risk: str
    overall_confidence: float
    agent_assessments: Dict[str, AgentAssessment]
    high_risk_clauses: List[Dict]
    recommended_actions: List[str]
    model_analysis: Dict
    formatted_report: Optional[str]
    processing_time_seconds: float


def load_refined_agent_outputs() -> Dict:
    combined_path = os.path.join(
        MILESTONE3_OUTPUT,
        "refined_agent_outputs_combined.json"
    )

    if not os.path.exists(combined_path):
        raise FileNotFoundError(
            "refined_agent_outputs_combined.json not found in Milestone3 output"
        )

    with open(combined_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["agents"]

def load_final_contract_analysis() -> Dict:
    final_path = os.path.join(
        MILESTONE3_OUTPUT,
        "final_contract_analysis_new.json"
    )

    if not os.path.exists(final_path):
        raise FileNotFoundError("final_contract_analysis_new.json not found")

    with open(final_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_final_report_text() -> Optional[str]:
    report_path = os.path.join(
        MILESTONE3_OUTPUT,
        "contract_analysis_report_new.txt"
    )

    if os.path.exists(report_path):
        with open(report_path, "r", encoding="utf-8") as f:
            return f.read()

    return None


def run_gemma2(prompt: str) -> str:

    try:
        result = subprocess.run(
            ["ollama", "run", "gemma2:9b"],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60000,
        )
        return result.stdout.decode("utf-8").strip()
    except Exception as e:
        return f"Model invocation failed: {str(e)}"

def generate_model_analysis(
    contract_text: str,
    refined_agents: Dict,
    final_analysis: Dict
) -> Dict:
   

    agent_snapshot = []
    escalations = []

    for agent, data in refined_agents.items():
        agent_snapshot.append(
            f"{agent.upper()} -> risk={data.get('risk_level')}, "
            f"confidence={data.get('confidence')}, "
            f"escalations={len(data.get('escalation_reasons', []))}"
        )
        escalations.extend(data.get("escalation_reasons", []))

    prompt = f"""
You are a contract risk analysis assistant.

Contract excerpt:
{contract_text[:800]}

Refined agent states:
{chr(10).join(agent_snapshot)}

Overall contract risk:
{final_analysis.get("overall_assessment", {}).get("overall_risk")}

Tasks:
1. Explain which agents are most relevant.
2. Explain cross-agent risk propagation.
3. Summarize why the overall risk is high or medium.
Return short bullet points.
"""

    model_text = run_gemma2(prompt)

    return {
        "agents_considered": list(refined_agents.keys()),
        "cross_agent_reasoning": model_text,
        "total_escalation_reasons": len(escalations),
    }


def run_full_pipeline(contract_text: str, tone: str) -> tuple:
    start_time = datetime.now()

    contract_id = hashlib.md5(contract_text.encode()).hexdigest()[:16]

    agents = load_refined_agent_outputs()
    final_analysis = load_final_contract_analysis()
    report_text = load_final_report_text()

    model_analysis = generate_model_analysis(
        contract_text,
        agents,
        final_analysis
    )

    processing_time = (datetime.now() - start_time).total_seconds()

    return (
        contract_id,
        final_analysis,
        agents,
        report_text,
        model_analysis,
        processing_time,
    )

@app.get("/")
async def root():
    return {
        "message": "Contract Analysis API – Milestone 3",
        "status": "operational",
        "outputs_directory": MILESTONE3_OUTPUT,
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "output_directory": MILESTONE3_OUTPUT,
    }

@app.post("/analyze", response_model=ContractAnalysisResponse)
async def analyze_contract(request: ContractAnalysisRequest):
    try:
        if not request.contract_text or len(request.contract_text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Contract text must be at least 100 characters",
            )

        (
            contract_id,
            final_json,
            agents,
            report_text,
            model_analysis,
            processing_time,
        ) = run_full_pipeline(request.contract_text, request.tone)

        overall = final_json["overall_assessment"]

        response_agents = {}
        for agent, data in agents.items():
            response_agents[agent] = {
                "agent_name": agent,
                "risk_level": data.get("risk_level", "unknown"),
                "confidence": data.get("confidence", 0.0),
                "num_clauses": data.get("num_clauses", 0),
                "is_refined": True,
                "escalation_reasons": data.get("escalation_reasons", []),
            }

        high_risk_clauses = final_json.get("high_risk_clauses", [])

        recommended_actions = final_json.get(
            "executive_summary", {}
        ).get("recommended_actions", [])

        return JSONResponse(
            content={
                "contract_id": contract_id,
                "generated_at": final_json.get("generated_at"),
                "overall_risk": overall.get("overall_risk"),
                "overall_confidence": overall.get("overall_confidence"),
                "agent_assessments": response_agents,
                "high_risk_clauses": high_risk_clauses,
                "recommended_actions": recommended_actions,
                "model_analysis": model_analysis,
                "formatted_report": report_text if request.include_report else None,
                "processing_time_seconds": round(processing_time, 2),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}",
        )

@app.post("/analyze/upload")
async def analyze_uploaded_file(
    file: UploadFile = File(...),
    tone: str = Query("executive"),
    include_report: bool = Query(True),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        contract_text = content.decode("utf-8")
    except UnicodeDecodeError:
        contract_text = content.decode("latin-1")

    request = ContractAnalysisRequest(
        contract_text=contract_text,
        tone=tone,
        include_report=include_report,
    )

    return await analyze_contract(request)

@app.post("/analyze/quick")
async def quick_analysis(contract_text: str = Body(..., embed=True)):
    request = ContractAnalysisRequest(
        contract_text=contract_text,
        tone="simple",
        include_report=True,
    )
    return await analyze_contract(request)


if __name__ == "__main__":
    import uvicorn

    print("CONTRACT ANALYSIS API")

    print(f"Output directory: {MILESTONE3_OUTPUT}")
    print("Docs: http://localhost:8000/docs")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

