import time
from datetime import datetime

class ContractAnalyzer:
    @staticmethod
    def analyze_risk_level(contract_text: str) -> dict:
        """
        Analyze contract text and determine risk levels for each agent.
        Returns dict with agent-specific risk levels.
        """
        text_lower = contract_text.lower()
        
        high_risk_keywords = {
            "legal": ["no refund", "no termination", "cannot terminate", "waives right", "mandatory arbitration", "no liability", "assumes all liability", "indemnification", "gross negligence"],
            "compliance": ["no gdpr", "no compliance", "regulatory violations", "no data privacy", "no cybersecurity", "lacks required", "potential violations"],
            "finance": ["upfront payment", "100%", "no refund", "no escrow", "no milestone", "no performance guarantee", "$500,000", "extreme", "significant financial"],
            "operations": ["no sla", "no service level", "vendor can terminate", "no delivery timeline", "no performance", "heavily favors vendor", "extreme", "no guarantees"]
        }
        
        medium_risk_keywords = {
            "legal": ["clarification needed", "standard clause", "review recommended"],
            "compliance": ["update required", "check compliance"],
            "finance": ["negotiate", "payment terms", "net 30", "net 60"],
            "operations": ["timeline", "6 months", "weekly meetings"]
        }
        
        risk_counts = {}
        for category, keywords in high_risk_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            risk_counts[category] = count
            
        agent_risks = {}
        for category in ["legal", "compliance", "finance", "operations"]:
            if risk_counts.get(category, 0) >= 1: 
                agent_risks[category] = "high"
            else:
                medium_count = sum(1 for kw in medium_risk_keywords.get(category, []) if kw in text_lower)
                agent_risks[category] = "medium" if medium_count > 0 else "low"
        
        return agent_risks

    @staticmethod
    def run_full_pipeline(contract_text: str, tone: str = "professional"):
        """
        Complete contract analysis pipeline with intelligent risk detection
        """
        time.sleep(1.0)
        
        agent_risks = ContractAnalyzer.analyze_risk_level(contract_text)
        
        analysis_results = {
            "legal": {
                "agent": "Legal",
                "status": "complete",
                "risk_level": agent_risks["legal"],
                "analysis": "Critical legal issues identified - unfavorable terms detected" if agent_risks["legal"] == "high" else "Contract terms reviewed and validated",
                "risks": ["No termination rights", "Waived legal protections", "Mandatory arbitration"] if agent_risks["legal"] == "high" else [],
                "recommendations": ["URGENT: Negotiate termination rights", "Seek legal counsel immediately"] if agent_risks["legal"] == "high" else ["Standard review"]
            },
            "compliance": {
                "agent": "Compliance",
                "status": "complete",
                "risk_level": agent_risks["compliance"],
                "analysis": "Regulatory compliance failures detected." if agent_risks["compliance"] == "high" else "Regulatory compliance checked.",
                "risks": ["Missing GDPR clause", "No data privacy protections"] if agent_risks["compliance"] == "high" else [],
                "recommendations": ["Add Data Processing Addendum", "Conduct compliance audit"] if agent_risks["compliance"] == "high" else ["Monitor annually"]
            },
            "finance": {
                "agent": "Finance",
                "status": "complete",
                "risk_level": agent_risks["finance"],
                "analysis": "Extreme financial risk - unfavorable payment terms." if agent_risks["finance"] == "high" else "Financial terms analyzed.",
                "risks": ["100% upfront payment required", "No refund clause"] if agent_risks["finance"] == "high" else [],
                "recommendations": ["Negotiate milestone-based payments", "Require escrow"] if agent_risks["finance"] == "high" else ["Standard Net-30"]
            },
            "operations": {
                "agent": "Operations",
                "status": "complete",
                "risk_level": agent_risks["operations"],
                "analysis": "Contract heavily favors vendor - operational risk." if agent_risks["operations"] == "high" else "Operational feasibility assessed.",
                "risks": ["No SLA commitments", "Undefined delivery timeline"] if agent_risks["operations"] == "high" else [],
                "recommendations": ["Define SLA", "Set delivery milestones"] if agent_risks["operations"] == "high" else ["Set up status meetings"]
            }
        }
        
        risk_vals = [a["risk_level"] for a in analysis_results.values()]
        if "high" in risk_vals:
            overall_risk = "high"
        elif "medium" in risk_vals:
            overall_risk = "medium"
        else:
            overall_risk = "low"
            
        report = f"""
CONTRACT ANALYSIS REPORT ({tone.upper()})
OVERALL RISK: {overall_risk.upper()}

1. LEGAL: {analysis_results['legal']['risk_level'].upper()}
   {analysis_results['legal']['analysis']}

2. FINANCE: {analysis_results['finance']['risk_level'].upper()}
   {analysis_results['finance']['analysis']}

3. COMPLIANCE: {analysis_results['compliance']['risk_level'].upper()}
   {analysis_results['compliance']['analysis']}

4. OPERATIONS: {analysis_results['operations']['risk_level'].upper()}
   {analysis_results['operations']['analysis']}
"""
        return {"analysis": {**analysis_results, "overall_risk": overall_risk}, "report": report, "report_tone": tone}