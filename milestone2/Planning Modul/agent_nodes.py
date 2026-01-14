from typing import TypedDict, List, Dict, Any
from datetime import datetime

# 1. Defining the GraphState (The Shared Memory)
class GraphState(TypedDict):
    query: str                       # The user's input question
    legal: Dict[str, Any]            # Findings from the Legal Agent
    compliance: Dict[str, Any]       # Findings from the Compliance Agent
    finance: Dict[str, Any]          # Findings from the Finance Agent
    operations: Dict[str, Any]       # Findings from the Operations Agent
    execution_order: List[str]       # Tracks which agent ran and when
    memory: List[Dict[str, Any]]     # Summary of results for inter-agent talk

    # 2. Define the Legal Agent Node
def legal_node(state: GraphState) -> GraphState:
    print("\n--- [EXECUTING LEGAL AGENT] ---")

    # In a real setup, this agent would search Pinecone here.
    # For Milestone 2 validation, we update the state.
    state["legal"] = {
        "status": "completed",
        "risk_assessment": "Medium",
        "found_clauses": ["Section 4.2: Termination for Cause"]
    }

    # Update execution tracking
    state["execution_order"].append("legal_agent")

    return state

# 3. Define the Compliance Agent Node
def compliance_node(state: GraphState) -> GraphState:
    print("\n--- [EXECUTING COMPLIANCE AGENT] ---")
    state["compliance"] = {
        "status": "completed",
        "regulations": ["GDPR Article 28", "Data Protection Act"],
        "risk_level": "High"
    }
    state["execution_order"].append("compliance_agent")
    state["memory"].append({
        "agent": "compliance",
        "summary": "Found high risk regarding data privacy clauses."
    })
    return state

# 4. Define the Finance Agent Node
def finance_node(state: GraphState) -> GraphState:
    print("\n--- [EXECUTING FINANCE AGENT] ---")
    state["finance"] = {
        "status": "completed",
        "payment_terms": "Net 30",
        "penalties": "2% late fee"
    }
    state["execution_order"].append("finance_agent")
    state["memory"].append({
        "agent": "finance",
        "summary": "Extracted payment terms and late fee penalties."
    })
    return state

# 5. Define the Operations Agent Node
def operations_node(state: GraphState) -> GraphState:
    print("\n--- [EXECUTING OPERATIONS AGENT] ---")
    state["operations"] = {
        "status": "completed",
        "delivery_timeline": "90 days",
        "sla_met": True
    }
    state["execution_order"].append("operations_agent")
    state["memory"].append({
        "agent": "operations",
        "summary": "Verified project delivery timelines and SLAs."
    })
    return state