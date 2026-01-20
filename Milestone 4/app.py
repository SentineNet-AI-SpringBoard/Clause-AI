from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import traceback
from database import init_db

init_db()

from database import create_user, get_user_by_email
from auth_utils import hash_password, verify_password
from engine import run_full_analysis

app = FastAPI(
    title="Contract Analysis API",
    description="Multi-Agent RAG Contract Risk Analysis with Cross-Refinement",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContractAnalysisRequest(BaseModel):
    contract_text: str
    tone: Optional[str] = "executive"
    include_report: Optional[bool] = True


class AgentAssessment(BaseModel):
    risk_level: str
    confidence: float
    num_clauses: int
    enhanced_analysis: str


class ContractAnalysisResponse(BaseModel):
    contract_id: str
    generated_at: str
    overall_risk: str
    overall_confidence: float
    agent_assessments: Dict[str, AgentAssessment]
    high_risk_clauses: List[Dict]
    execution_times: Dict
    processing_time_seconds: float
    status: str

class RecommendationSummaryResponse(BaseModel):
    overall_risk: str
    top_risks: List[str]
    priority_actions: List[Dict]
    negotiation_flags: List[str]
    executive_summary: str

@app.get("/")
async def root():
    return {
        "message": "Contract Analysis API – Multi-Agent RAG System",
        "status": "operational",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - Analyze contract text",
            "/analyze/upload": "POST - Upload and analyze contract file",
            "/health": "GET - Health check"
        }
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "engine": "ready"
        }
    }

@app.post("/auth/signup")
def signup(email: str, password: str):
    if get_user_by_email(email):
        raise HTTPException(status_code=400, detail="User already exists")

    create_user(email, hash_password(password))
    return {"status": "created"}

@app.post("/auth/login")
def login(email: str, password: str):
    user = get_user_by_email(email)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "user_id": user["id"],
        "email": user["email"]
    }


@app.post("/analyze", response_model=ContractAnalysisResponse)
async def analyze_contract(request: ContractAnalysisRequest):
 
    try:
        if not request.contract_text or len(request.contract_text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Contract text must be at least 100 characters",
            )
        
        print(f"\n{'='*60}")
        print(f"NEW ANALYSIS REQUEST")
        print(f"{'='*60}")
        print(f"Contract length: {len(request.contract_text)} characters")
        print(f"Tone: {request.tone}")
        
        analysis_results = run_full_analysis(request.contract_text)
        
        print(f"\nAnalysis completed successfully")
        print(f"Contract ID: {analysis_results['contract_id']}")
        print(f"Overall Risk: {analysis_results['overall_assessment']['overall_risk']}")
        print(f"Processing Time: {analysis_results['processing_time_seconds']:.2f}s")
        print(f"{'='*60}\n")
        
        return JSONResponse(
            content=analysis_results,
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\nERROR in analysis:")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}",
        )


@app.post("/analyze/upload")
async def analyze_uploaded_file(file: UploadFile = File(...)):
  
    try:
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        try:
            contract_text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                contract_text = content.decode("latin-1")
            except Exception:
                raise HTTPException(
                    status_code=400,
                    detail="Unable to decode file. Please upload a text file."
                )
        
        print(f"\n{'='*60}")
        print(f"FILE UPLOAD ANALYSIS")
        print(f"{'='*60}")
        print(f"Filename: {file.filename}")
        print(f"Content-Type: {file.content_type}")
        print(f"Size: {len(contract_text)} characters")
        
        if len(contract_text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Contract file must contain at least 100 characters"
            )
        
        analysis_results = run_full_analysis(contract_text)
        
        print(f"\nFile analysis completed")
        print(f"Contract ID: {analysis_results['contract_id']}")
        print(f"Overall Risk: {analysis_results['overall_assessment']['overall_risk']}")
        print(f"{'='*60}\n")
        
        return JSONResponse(
            content=analysis_results,
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\nERROR in file analysis:")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"File analysis failed: {str(e)}",
        )

@app.post("/recommendations/summary", response_model=RecommendationSummaryResponse)
async def recommendation_summary(request: ContractAnalysisRequest):
    analysis_results = run_full_analysis(request.contract_text)
    from engine import build_exec_recommendation_summary
    return build_exec_recommendation_summary(analysis_results)

@app.post("/analyze/quick")
async def quick_analysis(contract_text: str = Body(..., embed=True)):

    try:
        if len(contract_text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Contract text must be at least 100 characters"
            )
        
        print(f"\nQuick Analysis Request - {len(contract_text)} chars")
        
        analysis_results = run_full_analysis(contract_text)
        
        return {
            "contract_id": analysis_results["contract_id"],
            "overall_risk": analysis_results["overall_assessment"]["overall_risk"],
            "overall_confidence": analysis_results["overall_assessment"]["overall_confidence"],
            "processing_time": analysis_results["processing_time_seconds"],
            "agents": {
                agent: {
                    "risk": data["risk_level"],
                    "confidence": data["confidence"]
                }
                for agent, data in analysis_results["agent_assessments"].items()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Quick analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Quick analysis failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    print("CONTRACT ANALYSIS API")
    print("\nStarting server...")
    print("API Docs: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("\nPress CTRL+C to stop")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )