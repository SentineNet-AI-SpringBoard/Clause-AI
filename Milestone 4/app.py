from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime
import traceback
import json
import tempfile
import os
from utils.pdf_export import build_agent_recommendations_pdf
from database import init_db

init_db()

from database import (
    create_user, get_user_by_email, get_user_by_id,
    save_report, get_reports_for_user, get_report_by_id, delete_report
)
from auth_utils import hash_password, verify_password
from engine import run_full_analysis, build_human_readable_recommendations


app = FastAPI(
    title="Contract Analysis API",
    description="Multi-Agent RAG Contract Risk Analysis with Cross-Refinement",
    version="2.0.0",
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


class UserSignupRequest(BaseModel):
    email: str
    password: str


class UserLoginRequest(BaseModel):
    email: str
    password: str


class SaveReportRequest(BaseModel):
    user_id: int
    contract_name: str
    analysis: dict



@app.get("/")
async def root():
    return {
        "message": "Contract Analysis API — Multi-Agent RAG System",
        "status": "operational",
        "version": "2.0.0",
        "endpoints": {
            "/analyze": "POST - Analyze contract text",
            "/analyze/upload": "POST - Upload and analyze contract file",
            "/health": "GET - Health check",
            "/auth/signup": "POST - Create new user account",
            "/auth/login": "POST - Authenticate user",
            "/reports/save": "POST - Save analysis report",
            "/reports/user/{user_id}": "GET - Get user's reports",
            "/reports/download/{report_id}": "GET - Download report as JSON"
        }
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "engine": "ready",
            "database": "ready",
            "auth": "ready"
        }
    }


@app.post("/auth/signup")
def signup(request: UserSignupRequest):
    """Create a new user account"""
    if get_user_by_email(request.email):
        raise HTTPException(status_code=400, detail="User already exists")

    try:
        create_user(request.email, hash_password(request.password))
        return {
            "status": "created",
            "message": "Account created successfully",
            "email": request.email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Account creation failed: {str(e)}")


@app.post("/auth/login")
def login(request: UserLoginRequest):
    """Authenticate user and return user details"""
    user = get_user_by_email(request.email)
    
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "status": "success",
        "message": "Login successful",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "created_at": user["created_at"]
        }
    }



@app.post("/analyze", response_model=ContractAnalysisResponse)
async def analyze_contract(request: ContractAnalysisRequest):
    """Analyze contract text with multi-agent system"""
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
        
        analysis_results["human_readable_recommendations"] = (
            build_human_readable_recommendations(analysis_results)
        )

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
    """Upload and analyze contract file"""
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
        analysis_results["human_readable_recommendations"] = (
            build_human_readable_recommendations(analysis_results)
        )

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


@app.post("/analyze/quick")
async def quick_analysis(contract_text: str = Body(..., embed=True)):
    """Quick analysis returning minimal data"""
    try:
        if len(contract_text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Contract text must be at least 100 characters"
            )
        
        print(f"\nQuick Analysis Request - {len(contract_text)} chars")
        
        analysis_results = run_full_analysis(contract_text)
        analysis_results["human_readable_recommendations"] = (
            build_human_readable_recommendations(analysis_results)
        )

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



@app.post("/reports/save")
async def save_analysis_report(request: SaveReportRequest):
    """Save analysis report to database"""
    try:
        user = get_user_by_id(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        report_id = save_report(
                        request.user_id,
                        request.contract_name,
                        request.analysis
                    )

        return {
            "status": "success",
            "report_id": report_id,
            "contract_name": request.contract_name
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save report: {str(e)}"
        )


@app.get("/reports/user/{user_id}")
async def get_user_reports(user_id: int):
    """Get all reports for a specific user"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        reports = get_reports_for_user(user_id)
        
        report_list = []
        for report in reports:
            report_list.append({
                "id": report["id"],
                "contract_name": report["contract_name"],
                "created_at": report["created_at"],
                "analysis_preview": {
                    "contract_id": json.loads(report["analysis_json"]).get("contract_id"),
                    "overall_risk": json.loads(report["analysis_json"]).get("overall_assessment", {}).get("overall_risk")
                }
            })
        
        return {
            "status": "success",
            "user_id": user_id,
            "report_count": len(report_list),
            "reports": report_list
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve reports: {str(e)}"
        )


from starlette.background import BackgroundTask 

@app.get("/reports/download/{report_id}")
async def download_report(report_id: int):
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    analysis = json.loads(report["analysis_json"])
    
    recommendations_text = analysis.get("human_readable_recommendations")

    if not recommendations_text:
        raise HTTPException(status_code=400, detail="No recommendations found")

    fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    try:
        build_agent_recommendations_pdf(
            output_path=tmp_path,
            contract_name=report["contract_name"],
            recommendations_text=recommendations_text, 
        )
        
        return FileResponse(
            tmp_path,
            media_type="application/pdf",
            filename=f"Recommendations_{report_id}.pdf",
            background=BackgroundTask(lambda: os.remove(tmp_path))
        )
    finally:
        os.close(fd)

@app.delete("/reports/delete/{report_id}")
async def delete_user_report(report_id: int, user_id: int = Body(..., embed=True)):
    """Delete a specific report"""
    try:
        delete_report(report_id, user_id)
        return {
            "status": "success",
            "message": "Report deleted successfully",
            "report_id": report_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete report: {str(e)}"
        )



@app.post("/recommendations/summary", response_model=RecommendationSummaryResponse)
async def recommendation_summary(request: ContractAnalysisRequest):
    """Generate executive recommendation summary"""
    analysis_results = run_full_analysis(request.contract_text)
    from engine import build_exec_recommendation_summary
    return build_exec_recommendation_summary(analysis_results)

@app.get("/reports/full/{report_id}")
async def get_full_report(report_id: int):
    """Retrieve full analysis JSON for a specific report"""
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    analysis = json.loads(report["analysis_json"])
    
    return {
        "id": report["id"],
        "contract_name": report["contract_name"],
        "created_at": report["created_at"],
        "analysis": analysis
    }

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("CONTRACT ANALYSIS API")
    print("=" * 60)
    print("\nStarting server...")
    print("API Docs: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("Auth Enabled: Yes")
    print("Database: SQLite (clauseai.db)")
    print("\nPress CTRL+C to stop")

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )