import operator
import os
import json
import time
import re
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, TypedDict, Annotated
from concurrent.futures import ThreadPoolExecutor, as_completed

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from langgraph.graph import StateGraph, END

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', 'pcsk_3ftgmC_GzUZkRCnxa2jmDu7TTjnGWjC3QaN8c2PcQ5KN5PUSyQaEmmcdGUGu2BLd4Y7TRn')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'gemma2:9b')
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/generate')

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("contract-agents")

def merge_dicts(existing: dict, new: dict) -> dict:
    return {**existing, **new}

class AgentState(TypedDict):
    query: str
    contract_text: str
    routing_decision: dict
    legal_output: dict
    compliance_output: dict
    finance_output: dict
    operations_output: dict
    execution_times: Annotated[dict, merge_dicts]
    agent_status: Annotated[dict, merge_dicts]
    completion_timestamps: Annotated[dict, merge_dicts]
    all_clauses: Annotated[list, operator.add] 
    timestamp: str
    status: str


def call_ollama(prompt: str, max_tokens: int = 500) -> str:
   
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=12000)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', '').strip()
    except Exception as e:
        print(f"Ollama API error: {e}")
        return ""

def safe_json_parse(text: str) -> dict:

    try:
        cleaned = re.sub(r"```(?:json)?", "", text).strip()

        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if not match:
            raise ValueError("No JSON object found")

        json_str = match.group(0)
        return json.loads(json_str)

    except Exception as e:
        print(f"[JSON PARSE FAILED] {e}")
        return {
            "risk_level": "unknown",
            "key_concerns": [],
            "recommendations": []
        }


def load_agent_output_from_pinecone(agent_name: str) -> dict:
    try:
        query_embedding = [0.0] * 384
        
        target_namespace = "" 
        
        results = index.query(
            vector=query_embedding,
            filter={"agent": agent_name}, 
            namespace=target_namespace,
            top_k=10,
            include_metadata=True
        )
        
        if results.matches and len(results.matches) > 0:
            agent_clauses = []
            for match in results.matches:
                m = match.metadata
                clause_text = (
                    m.get('clause_full') or 
                    m.get('clause') or 
                    'No text found'
                )
                
                agent_clauses.append({
                    'clause': clause_text,
                    'clause_index': m.get('clause_index', 0),
                    'risk_level': m.get('risk_level', 'unknown'),
                    'confidence': m.get('confidence', 0),
                    'timestamp': m.get('timestamp', '')
                })
            
            return {
                'agent': agent_name,
                'clauses': agent_clauses,
                'risk_level': results.matches[0].metadata.get('risk_level', 'unknown'),
                'confidence': results.matches[0].metadata.get('confidence', 0),
                'timestamp': results.matches[0].metadata.get('timestamp', '')
            }
        return None
    except Exception as e:
        print(f"Error loading {agent_name} output: {e}")
        return None


def legal_agent_node(state: AgentState) -> dict:
    start_time = time.time()
    print(f"  → Legal Agent executing...")
    
    legal_data = load_agent_output_from_pinecone("legal")
    
    if not legal_data:
        execution_time = time.time() - start_time
        return {
            "legal_output": {
                "risk_level": "unknown", 
                "confidence": 0, 
                "clauses": [], 
                "enhanced_analysis": "No legal clauses found in database."
            },
            "execution_times": {"legal": execution_time},
            "agent_status": {"legal": "completed"},
            "completion_timestamps": {"legal": datetime.now().isoformat()},
            "all_clauses": []
        }
    
    clauses_text = "\n".join([c['clause'] for c in legal_data.get('clauses', [])])
    
    prompt = f"""Analyze these legal clauses and provide risk assessment:

Clauses:
{clauses_text}

Return valid JSON with the following structure:
{{
  "risk_level": "low | medium | high",
  "key_concerns": [string],
  "recommendations": [string]
}}

Response:"""
    
    analysis = call_ollama(prompt, max_tokens=4000)
    parsed = safe_json_parse(analysis)

    legal_data["risk_level"] = parsed["risk_level"]
    legal_data["key_concerns"] = parsed["key_concerns"]
    legal_data["recommendations"] = parsed["recommendations"]
    legal_data["enhanced_analysis"] = analysis

    legal_data['enhanced_analysis'] = analysis
    legal_data['model_used'] = OLLAMA_MODEL
    
    execution_time = time.time() - start_time
    print(f"  Legal Agent completed in {execution_time:.3f}s")

    return {
        "legal_output": legal_data,
        "execution_times": {"legal": execution_time},
        "agent_status": {"legal": "completed"},
        "completion_timestamps": {"legal": datetime.now().isoformat()},
        "all_clauses": legal_data.get('clauses', [])
    }

def compliance_agent_node(state: AgentState) -> dict:
    start_time = time.time()
    print(f"  → Compliance Agent executing...")
    
    compliance_data = load_agent_output_from_pinecone("compliance")
    
    if not compliance_data:
        execution_time = time.time() - start_time
        return {
            "compliance_output": {
                "risk_level": "unknown", 
                "confidence": 0, 
                "clauses": [], 
                "enhanced_analysis": "No compliance clauses found."
            },
            "execution_times": {"compliance": execution_time},
            "agent_status": {"compliance": "completed"},
            "completion_timestamps": {"compliance": datetime.now().isoformat()},
            "all_clauses": []
        }
    
    clauses_text = "\n".join([c['clause'] for c in compliance_data.get('clauses', [])])
    
    prompt = f"""Analyze these compliance clauses for GDPR and data protection risks:

Clauses:
{clauses_text}

Return valid JSON with the following structure:
{{
  "risk_level": "low | medium | high",
  "key_concerns": [string],
  "recommendations": [string]
}}

Response:"""
    
    analysis = call_ollama(prompt, max_tokens=4000)
    parsed = safe_json_parse(analysis)

    compliance_data["risk_level"] = parsed["risk_level"]
    compliance_data["key_concerns"] = parsed["key_concerns"]
    compliance_data["recommendations"] = parsed["recommendations"]
    compliance_data["enhanced_analysis"] = analysis

    compliance_data['enhanced_analysis'] = analysis
    compliance_data['model_used'] = OLLAMA_MODEL
    
    execution_time = time.time() - start_time
    print(f"  Compliance Agent completed in {execution_time:.3f}s")

    return {
        "compliance_output": compliance_data,
        "execution_times": {"compliance": execution_time},
        "agent_status": {"compliance": "completed"},
        "completion_timestamps": {"compliance": datetime.now().isoformat()},
        "all_clauses": compliance_data.get('clauses', [])
    }

def finance_agent_node(state: AgentState) -> dict:
    start_time = time.time()
    print(f"  → Finance Agent executing...")
    
    finance_data = load_agent_output_from_pinecone("finance")
    
    if not finance_data:
        execution_time = time.time() - start_time
        return {
            "finance_output": {
                "risk_level": "unknown", 
                "confidence": 0, 
                "clauses": [], 
                "enhanced_analysis": "No financial clauses found."
            },
            "execution_times": {"finance": execution_time},
            "agent_status": {"finance": "completed"},
            "completion_timestamps": {"finance": datetime.now().isoformat()},
            "all_clauses": []
        }
    
    clauses_text = "\n".join([c['clause'] for c in finance_data.get('clauses', [])])
    
    prompt = f"""Analyze these financial clauses for payment risks:

Clauses:
{clauses_text}

Return valid JSON with the following structure:
{{
  "risk_level": "low | medium | high",
  "key_concerns": [string],
  "recommendations": [string]
}}

Response:"""
    
    analysis = call_ollama(prompt, max_tokens=4000)
    
    parsed = safe_json_parse(analysis)

    finance_data["risk_level"] = parsed["risk_level"]
    finance_data["key_concerns"] = parsed["key_concerns"]
    finance_data["recommendations"] = parsed["recommendations"]
    finance_data["enhanced_analysis"] = analysis

    finance_data['enhanced_analysis'] = analysis
    finance_data['model_used'] = OLLAMA_MODEL
    
    execution_time = time.time() - start_time
    print(f"  Finance Agent completed in {execution_time:.3f}s")

    return {
        "finance_output": finance_data,
        "execution_times": {"finance": execution_time},
        "agent_status": {"finance": "completed"},
        "completion_timestamps": {"finance": datetime.now().isoformat()},
        "all_clauses": finance_data.get('clauses', [])
    }


def operations_agent_node(state: AgentState) -> dict:
   
    start_time = time.time()
    print(f"  → Operations Agent executing...")
    
    operations_data = load_agent_output_from_pinecone("operations")
    
    if not operations_data:
        execution_time = time.time() - start_time
        return {
            "operations_output": {
                "risk_level": "unknown", 
                "confidence": 0, 
                "clauses": [], 
                "enhanced_analysis": "No operational clauses found."
            },
            "execution_times": {"operations": execution_time},
            "agent_status": {"operations": "completed"},
            "completion_timestamps": {"operations": datetime.now().isoformat()},
            "all_clauses": []
        }
    
    clauses_text = "\n".join([c['clause'] for c in operations_data.get('clauses', [])])
    
    prompt = f"""Analyze these operational clauses:

Clauses:
{clauses_text}

Return valid JSON with the following structure:
{{
  "risk_level": "low | medium | high",
  "key_concerns": [string],
  "recommendations": [string]
}}

Response:"""
    
    analysis = call_ollama(prompt, max_tokens=4000)
    
    parsed = safe_json_parse(analysis)

    operations_data["risk_level"] = parsed["risk_level"]
    operations_data["key_concerns"] = parsed["key_concerns"]
    operations_data["recommendations"] = parsed["recommendations"]
    operations_data["enhanced_analysis"] = analysis

    operations_data['enhanced_analysis'] = analysis
    operations_data['model_used'] = OLLAMA_MODEL
    
    execution_time = time.time() - start_time
    print(f"  Operations Agent completed in {execution_time:.3f}s")

    return {
        "operations_output": operations_data,
        "execution_times": {"operations": execution_time},
        "agent_status": {"operations": "completed"},
        "completion_timestamps": {"operations": datetime.now().isoformat()},
        "all_clauses": operations_data.get('clauses', [])
    }


def coordinator_node(state: AgentState) -> AgentState:
    
    print("\n  → Coordinator executing...")
    
    routing_decision = {
        "agents": ["legal", "compliance", "finance", "operations"],
        "reasoning": "Comprehensive contract analysis across all domains",
        "priority": "high",
        "timestamp": datetime.now().isoformat(),
        "model": OLLAMA_MODEL
    }
    
    state['routing_decision'] = routing_decision
    
    for agent in routing_decision['agents']:
        state['agent_status'][agent] = 'pending'
    
    return state


def build_workflow() -> StateGraph:
 
    workflow = StateGraph(AgentState)
    
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("legal_agent", legal_agent_node)
    workflow.add_node("compliance_agent", compliance_agent_node)
    workflow.add_node("finance_agent", finance_agent_node)
    workflow.add_node("operations_agent", operations_agent_node)
    
    workflow.set_entry_point("coordinator")
    
    workflow.add_edge("coordinator", "legal_agent")
    workflow.add_edge("coordinator", "compliance_agent")
    workflow.add_edge("coordinator", "finance_agent")
    workflow.add_edge("coordinator", "operations_agent")
    
    workflow.add_edge("legal_agent", END)
    workflow.add_edge("compliance_agent", END)
    workflow.add_edge("finance_agent", END)
    workflow.add_edge("operations_agent", END)
    
    return workflow


def calculate_overall_risk(agent_outputs: Dict) -> Dict:
    risk_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1, "unknown": 0}
    
    weighted_scores = []
    risk_distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    
    for agent_name in ['legal', 'compliance', 'finance', 'operations']:
        output = agent_outputs.get(f'{agent_name}_output', {})
        if output:
            risk_level = output.get('risk_level', 'unknown').lower()
            confidence = output.get('confidence', 0.0)
            
            weight = risk_weights.get(risk_level, 0)
            weighted_scores.append(weight * confidence)
            
            if risk_level in risk_distribution:
                risk_distribution[risk_level] += 1
    
    avg_weighted_score = sum(weighted_scores) / len(weighted_scores) if weighted_scores else 0
    
    if avg_weighted_score >= 3.5:
        overall_risk = "CRITICAL"
    elif avg_weighted_score >= 2.5:
        overall_risk = "HIGH"
    elif avg_weighted_score >= 1.5:
        overall_risk = "MEDIUM"
    else:
        overall_risk = "LOW"
    
    return {
        "overall_risk": overall_risk,
        "overall_confidence": avg_weighted_score / 4.0,
        "weighted_score": avg_weighted_score,
        "risk_distribution": risk_distribution
    }

def synthesize_recommendations(final_state: dict) -> dict:
    by_agent = {}
    priority_actions = []

    for agent in ["legal", "compliance", "finance", "operations"]:
        output = final_state.get(f"{agent}_output", {})
        recs = output.get("recommendations", [])

        by_agent[agent] = recs

        for r in recs:
            priority_actions.append({
                "action": r,
                "severity": output.get("risk_level", "unknown").upper(),
                "affected_agents": [agent]
            })

    return {
        "by_agent": by_agent,
        "priority_actions": priority_actions,
        "risk_mitigation_summary":
            "Prioritize remediation of high-risk financial reimbursements, "
            "third-party disclosures, and licensing obligations."
    }
    
def build_exec_recommendation_summary(result: Dict) -> Dict:
    agent_assessments = result.get("agent_assessments", {})
    high_risk_clauses = result.get("high_risk_clauses", [])

    top_risks = []
    priority_actions = []

    for agent, data in agent_assessments.items():
        if data.get("risk_level", "").lower() in {"high", "critical"}:
            top_risks.append(
                f"{agent.capitalize()} risk is HIGH with {data.get('num_clauses', 0)} concerning clauses."
            )

        if data.get("enhanced_analysis"):
            priority_actions.append({
                "agent": agent,
                "action": data["enhanced_analysis"][:180]
            })

    return {
        "overall_risk": result["overall_assessment"]["overall_risk"],
        "top_risks": top_risks[:3],
        "priority_actions": priority_actions[:5],
        "negotiation_flags": [c["clause"] for c in high_risk_clauses[:3]],
        "executive_summary":
            "This contract presents material risk exposure requiring remediation prior to execution."
    }

def run_full_analysis(contract_text: str) -> Dict:

    start_time = time.time()
    
    contract_id = hashlib.md5(contract_text.encode()).hexdigest()[:16]
    
    initial_state = {
        "query": "Analyze contract for all risk domains",
        "contract_text": contract_text,
        "routing_decision": {},
        "legal_output": {},
        "compliance_output": {},
        "finance_output": {},
        "operations_output": {},
        "execution_times": {},
        "agent_status": {},
        "completion_timestamps": {},
        "all_clauses": [],
        "timestamp": datetime.now().isoformat(),
        "status": "running"
    }
    
    workflow = build_workflow()
    app = workflow.compile()
    
    print("\nExecuting Parallel Agent Analysis...")
    final_state = app.invoke(initial_state)
    
    overall_assessment = calculate_overall_risk(final_state)
    
    recommendations = synthesize_recommendations(final_state)
    
    processing_time = time.time() - start_time
    
    result = {
        "contract_id": contract_id,
        "generated_at": datetime.now().isoformat(),
        "overall_assessment": overall_assessment,
        "agent_assessments": {
            "legal": {
                "risk_level": final_state['legal_output'].get('risk_level', 'unknown'),
                "confidence": final_state['legal_output'].get('confidence', 0),
                "num_clauses": len(final_state['legal_output'].get('clauses', [])),
                "enhanced_analysis": final_state['legal_output'].get('enhanced_analysis', '')
            },
            "compliance": {
                "risk_level": final_state['compliance_output'].get('risk_level', 'unknown'),
                "confidence": final_state['compliance_output'].get('confidence', 0),
                "num_clauses": len(final_state['compliance_output'].get('clauses', [])),
                "enhanced_analysis": final_state['compliance_output'].get('enhanced_analysis', '')
            },
            "finance": {
                "risk_level": final_state['finance_output'].get('risk_level', 'unknown'),
                "confidence": final_state['finance_output'].get('confidence', 0),
                "num_clauses": len(final_state['finance_output'].get('clauses', [])),
                "enhanced_analysis": final_state['finance_output'].get('enhanced_analysis', '')
            },
            "operations": {
                "risk_level": final_state['operations_output'].get('risk_level', 'unknown'),
                "confidence": final_state['operations_output'].get('confidence', 0),
                "num_clauses": len(final_state['operations_output'].get('clauses', [])),
                "enhanced_analysis": final_state['operations_output'].get('enhanced_analysis', '')
            }
        },
        "high_risk_clauses": [
            clause for clause in final_state['all_clauses'] 
            if clause.get('risk_level', '').lower() in ['high', 'critical']
        ],
        "recommendations": recommendations,
        "execution_times": final_state['execution_times'],
        "processing_time_seconds": round(processing_time, 2),
        "status": "completed"
    }
    
    return result

def build_human_readable_recommendations(result: Dict) -> str:
    recommendations = result.get("recommendations", {}).get("by_agent", {})
    overall_risk = result.get("overall_assessment", {}).get("overall_risk", "UNKNOWN")

    lines = []
    lines.append("CONTRACT REVIEW")
    lines.append(f"Overall Risk Assessment: {overall_risk}")
    lines.append("")

    for agent, recs in recommendations.items():
        if not recs:
            continue

        lines.append(f"{agent.upper()} RECOMMENDATIONS")

        for i, rec in enumerate(recs, 1):
            lines.append(f"{i}. {rec}")

        lines.append("")

    if len(lines) <= 5:
        lines.append("No actionable recommendations identified.")

    return "\n".join(lines)
