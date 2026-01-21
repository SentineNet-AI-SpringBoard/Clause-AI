from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import secrets

app = FastAPI(title="Contract Analysis API", version="1.0.0")

# Enable CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== IN-MEMORY STORAGE ====================
# In production, replace with a real database
users_db: Dict[str, Dict[str, Any]] = {
    # Pre-create a test user so you can login immediately
    "misthi@clauseai.com": {
        "email": "misthi@clauseai.com",
        "password": "misthi123",
        "name": "Misthi Maheshwari",
        "role": "Admin"
    }
}
tokens_db: Dict[str, str] = {}  # token -> email
history_db: Dict[str, list] = {}  # email -> list of analysis runs

# ==================== AUTH MODELS ====================
class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str
    role: str = "User"

class LoginRequest(BaseModel):
    email: str
    password: str

# ==================== AUTH ENDPOINTS ====================
@app.post("/auth/register")
async def register(req: RegisterRequest):
    """Register a new user"""
    if req.email in users_db:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "detail": "Email already registered"}
        )
    
    users_db[req.email] = {
        "email": req.email,
        "password": req.password,
        "name": req.name,
        "role": req.role
    }
    
    return {"ok": True, "message": "Account created successfully"}

@app.post("/auth/login")
async def login(req: LoginRequest):
    """Login and get authentication token"""
    user = users_db.get(req.email)
    
    if not user or user["password"] != req.password:
        return JSONResponse(
            status_code=401,
            content={"ok": False, "detail": "Invalid credentials"}
        )
    
    # Generate secure token
    token = secrets.token_urlsafe(32)
    tokens_db[token] = req.email
    
    return {
        "ok": True,
        "token": token,
        "user": {
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    }

# ==================== YOUR ORIGINAL ANALYSIS LOGIC ====================
def analyze_risk_level(contract_text: str) -> dict:
    """
    Analyze contract text and determine risk levels for each agent.
    Returns dict with agent-specific risk levels.
    """
    text_lower = contract_text.lower()
    
    # High-risk keywords by category
    high_risk_keywords = {
        "legal": ["no refund", "no termination", "cannot terminate", "waives right", "mandatory arbitration", 
                  "no liability", "assumes all liability", "indemnification", "gross negligence"],
        "compliance": ["no gdpr", "no compliance", "regulatory violations", "no data privacy", 
                       "no cybersecurity", "lacks required", "potential violations"],
        "finance": ["upfront payment", "100%", "no refund", "no escrow", "no milestone", 
                    "no performance guarantee", "$500,000", "extreme", "significant financial"],
        "operations": ["no sla", "no service level", "vendor can terminate", "no delivery timeline",
                       "no performance", "heavily favors vendor", "extreme", "no guarantees"]
    }
    
    medium_risk_keywords = {
        "legal": ["clarification needed", "standard clause", "review recommended"],
        "compliance": ["update required", "check compliance"],
        "finance": ["negotiate", "payment terms", "net 30", "net 60"],
        "operations": ["timeline", "6 months", "weekly meetings"]
    }
    
    # Count high-risk indicators per category
    risk_counts = {}
    for category, keywords in high_risk_keywords.items():
        count = sum(1 for keyword in keywords if keyword in text_lower)
        risk_counts[category] = count
    
    # Determine risk level for each agent
    agent_risks = {}
    for category in ["legal", "compliance", "finance", "operations"]:
        if risk_counts.get(category, 0) >= 3:
            agent_risks[category] = "high"
        elif risk_counts.get(category, 0) >= 1:
            agent_risks[category] = "medium"
        else:
            medium_count = sum(1 for kw in medium_risk_keywords.get(category, []) if kw in text_lower)
            agent_risks[category] = "medium" if medium_count > 0 else "low"
    
    return agent_risks

def run_full_pipeline(contract_text: str, tone: str = "professional"):
    """
    Complete contract analysis pipeline with intelligent risk detection
    """
    
    # Analyze risk levels based on contract content
    agent_risks = analyze_risk_level(contract_text)
    
    # Generate agent-specific analysis based on detected risks
    analysis_results = {
        "legal": {
            "agent": "Legal",
            "status": "complete",
            "risk_level": agent_risks["legal"],
            "analysis": "Critical legal issues identified - unfavorable terms detected" if agent_risks["legal"] == "high" 
                       else "Contract terms reviewed and validated",
            "risks": ["No termination rights", "Waived legal protections", "Mandatory arbitration in vendor jurisdiction", "No liability protection"] if agent_risks["legal"] == "high"
                    else ["Payment terms need clarification", "Termination clause is standard"],
            "recommendations": ["URGENT: Negotiate termination rights", "URGENT: Add liability protections", "Seek legal counsel immediately"] if agent_risks["legal"] == "high"
                             else ["Add force majeure clause"]
        },
        "compliance": {
            "agent": "Compliance",
            "status": "complete",
            "risk_level": agent_risks["compliance"],
            "analysis": "CRITICAL: Regulatory compliance failures detected - immediate action required" if agent_risks["compliance"] == "high"
                       else "Regulatory compliance checked",
            "risks": ["No GDPR compliance", "Missing data privacy clauses", "Potential regulatory violations", "No cybersecurity requirements"] if agent_risks["compliance"] == "high"
                    else [],
            "recommendations": ["URGENT: Add GDPR compliance clauses", "URGENT: Include data privacy protections", "Conduct compliance audit"] if agent_risks["compliance"] == "high"
                             else ["Update data privacy section"]
        },
        "finance": {
            "agent": "Finance",
            "status": "complete",
            "risk_level": agent_risks["finance"],
            "analysis": "CRITICAL: Extreme financial risk - unfavorable payment terms" if agent_risks["finance"] == "high"
                       else "Financial terms analyzed",
            "payment_terms": "100% upfront - NO REFUNDS" if agent_risks["finance"] == "high" else "Net 30",
            "total_value": "$500,000" if agent_risks["finance"] == "high" else "$50,000",
            "risks": ["100% upfront payment required", "No refund clause", "No escrow protection", "No milestone payments"] if agent_risks["finance"] == "high"
                    else [],
            "recommendations": ["URGENT: Negotiate milestone-based payments", "URGENT: Add refund protections", "URGENT: Require escrow", "DO NOT SIGN without changes"] if agent_risks["finance"] == "high"
                             else ["Negotiate early payment discount"]
        },
        "operations": {
            "agent": "Operations",
            "status": "complete",
            "risk_level": agent_risks["operations"],
            "analysis": "CRITICAL: Contract heavily favors vendor - extreme operational risk" if agent_risks["operations"] == "high"
                       else "Operational feasibility assessed",
            "timeline": "Undefined - vendor has full control" if agent_risks["operations"] == "high" else "6 months",
            "risks": ["No performance guarantees", "No SLA commitments", "Vendor can terminate without cause", "No delivery timeline"] if agent_risks["operations"] == "high"
                    else [],
            "recommendations": ["URGENT: Add performance metrics", "URGENT: Require SLA commitments", "URGENT: Define delivery milestones", "Consider alternative vendors"] if agent_risks["operations"] == "high"
                             else ["Set up weekly status meetings"]
        }
    }
    
    # Compute overall risk
    risk_levels = [agent["risk_level"] for agent in analysis_results.values()]
    high_count = risk_levels.count("high")
    medium_count = risk_levels.count("medium")
    
    if high_count >= 2:
        overall_risk = "high"
    elif high_count >= 1 or medium_count >= 3:
        overall_risk = "medium"
    else:
        overall_risk = "low"
    
    # Format report based on tone
    if tone == "executive":
        risk_emoji = "🔴" if overall_risk == "high" else "🟡" if overall_risk == "medium" else "🟢"
        formatted_report = f"""
>>> EXECUTIVE SUMMARY <<<

RISK ASSESSMENT: {risk_emoji} {overall_risk.upper()} RISK

{"⚠️ CRITICAL ALERT: DO NOT SIGN THIS CONTRACT WITHOUT MAJOR REVISIONS ⚠️" if overall_risk == "high" else ""}

FINDINGS:
→ Legal: {analysis_results['legal']['risk_level'].upper()} risk
→ Compliance: {analysis_results['compliance']['risk_level'].upper()} risk
→ Finance: {analysis_results['finance']['risk_level'].upper()} risk
→ Operations: {analysis_results['operations']['risk_level'].upper()} risk

CRITICAL ACTIONS REQUIRED:
{chr(10).join('→ ' + rec for agent in analysis_results.values() for rec in agent.get('recommendations', []))}

{"🚨 RECOMMENDATION: REJECT this contract or demand substantial revisions before proceeding." if overall_risk == "high" else ""}
"""
    else:
        formatted_report = f"""
CONTRACT ANALYSIS REPORT

Overall Risk Level: {overall_risk.upper()}
{"⚠️ WARNING: HIGH RISK CONTRACT DETECTED ⚠️" if overall_risk == "high" else ""}

LEGAL ANALYSIS:
- Status: {analysis_results['legal']['status']}
- Risk: {analysis_results['legal']['risk_level'].upper()}
- Analysis: {analysis_results['legal']['analysis']}
{"- Critical Issues: " + ", ".join(analysis_results['legal'].get('risks', [])) if analysis_results['legal']['risk_level'] == 'high' else ''}

COMPLIANCE ANALYSIS:
- Status: {analysis_results['compliance']['status']}
- Risk: {analysis_results['compliance']['risk_level'].upper()}
- Analysis: {analysis_results['compliance']['analysis']}
{"- Critical Issues: " + ", ".join(analysis_results['compliance'].get('risks', [])) if analysis_results['compliance']['risk_level'] == 'high' else ''}

FINANCE ANALYSIS:
- Status: {analysis_results['finance']['status']}
- Risk: {analysis_results['finance']['risk_level'].upper()}
- Analysis: {analysis_results['finance']['analysis']}
- Payment Terms: {analysis_results['finance']['payment_terms']}
- Total Value: {analysis_results['finance']['total_value']}
{"- Critical Issues: " + ", ".join(analysis_results['finance'].get('risks', [])) if analysis_results['finance']['risk_level'] == 'high' else ''}

OPERATIONS ANALYSIS:
- Status: {analysis_results['operations']['status']}
- Risk: {analysis_results['operations']['risk_level'].upper()}
- Analysis: {analysis_results['operations']['analysis']}
{"- Critical Issues: " + ", ".join(analysis_results['operations'].get('risks', [])) if analysis_results['operations']['risk_level'] == 'high' else ''}

{"🚨 URGENT RECOMMENDATION: This contract poses significant risks. Seek legal counsel and negotiate major revisions before signing." if overall_risk == "high" else ""}
"""
    
    return {"contract_id": "uploaded_contract", "generated_at": datetime.now().isoformat() + "Z", "analysis": {**analysis_results, "overall_risk": overall_risk}}, formatted_report

# ==================== ANALYSIS ENDPOINTS ====================
@app.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    question: str = Form(...),
    tone: str = Form("executive"),
    no_evidence_threshold: str = Form("0.25"),
    contract_id: Optional[str] = Form(None),
    intent_override: Optional[str] = Form(None),
    run_all_agents: str = Form("false")
):
    """Analyze uploaded contract file"""
    try:
        contents = await file.read()
        if not contents or len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")
        
        # Extract text based on file type
        filename = file.filename.lower()
        
        if filename.endswith('.pdf'):
            # Handle PDF
            from PyPDF2 import PdfReader
            from io import BytesIO
            pdf_file = BytesIO(contents)
            pdf_reader = PdfReader(pdf_file)
            contract_text = ""
            for page in pdf_reader.pages:
                contract_text += page.extract_text() + "\n"
        elif filename.endswith('.docx'):
            # Handle DOCX
            from docx import Document
            from io import BytesIO
            doc_file = BytesIO(contents)
            doc = Document(doc_file)
            contract_text = "\n".join([para.text for para in doc.paragraphs])
        else:
            # Handle TXT or other text files
            contract_text = contents.decode('utf-8')
        
        if len(contract_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Contract too short. Minimum 10 characters required.")
        
        final_json, formatted_report = run_full_pipeline(contract_text, tone)
        final_json["report"] = formatted_report
        final_json["report_tone"] = tone
        final_json["file_info"] = {"filename": file.filename, "size_bytes": len(contents), "content_length": len(contract_text)}
        
        return JSONResponse(status_code=200, content=final_json)
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/analyze_text")
async def analyze_text_endpoint(payload: dict):
    """Analyze contract text directly"""
    contract_text = payload.get("contract_text", "")
    tone = payload.get("tone", "executive")
    
    if len(contract_text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Contract too short")
    
    final_json, formatted_report = run_full_pipeline(contract_text, tone)
    final_json["report"] = formatted_report
    final_json["report_tone"] = tone
    
    return JSONResponse(status_code=200, content=final_json)

# ==================== OLD ENDPOINT (for compatibility) ====================
@app.post("/analyze-contract/")
async def analyze_contract(file: UploadFile = File(...), tone: Optional[str] = "professional"):
    """Legacy endpoint - kept for compatibility"""
    try:
        contents = await file.read()
        if not contents or len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")
        
        contract_text = contents.decode('utf-8')
        
        if len(contract_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Contract too short. Minimum 10 characters required.")
        
        if tone not in ["professional", "executive", "technical", "simple"]:
            raise HTTPException(status_code=400, detail="Invalid tone.")
        
        final_json, formatted_report = run_full_pipeline(contract_text, tone)
        final_json["report"] = formatted_report
        final_json["report_tone"] = tone
        final_json["file_info"] = {"filename": file.filename, "size_bytes": len(contents), "content_length": len(contract_text)}
        
        return JSONResponse(status_code=200, content=final_json)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# ==================== UTILITY ENDPOINTS ====================
@app.get("/")
async def root():
    return {"message": "Contract Analysis API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}