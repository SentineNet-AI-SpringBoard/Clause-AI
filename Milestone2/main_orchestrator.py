import json
from typing import List, Dict, Any
from typing_extensions import TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, END

# ==========================================
# SHARED STATE DEFINITION
# ==========================================
class GraphState(TypedDict):
    query: str
    legal: Dict[str, Any]
    compliance: Dict[str, Any]
    finance: Dict[str, Any]
    operations: Dict[str, Any]
    execution_order: List[str]
    memory: List[Dict[str, Any]]

# ==========================================
# AGENT NODES
# ==========================================
def legal_node(state: GraphState) -> GraphState:
    print("\n--- [EXECUTING LEGAL AGENT] ---")
    state["legal"] = {
        "status": "completed",
        "risk_assessment": "Medium",
        "found_clauses": ["Section 4.2: Termination for Cause"]
    }
    state["execution_order"].append("legal_agent")
    return state

def compliance_node(state: GraphState) -> GraphState:
    print("\n--- [EXECUTING COMPLIANCE AGENT] ---")
    state["compliance"] = {
        "status": "completed",
        "regulations": ["GDPR Article 28"],
        "risk_level": "High"
    }
    state["execution_order"].append("compliance_agent")
    return state

def finance_node(state: GraphState) -> GraphState:
    print("\n--- [EXECUTING FINANCE AGENT] ---")
    state["finance"] = {
        "status": "completed",
        "payment_terms": "Net 30",
        "penalties": "2% late fee"
    }
    state["execution_order"].append("finance_agent")
    return state

def operations_node(state: GraphState) -> GraphState:
    print("\n--- [EXECUTING OPERATIONS AGENT] ---")
    state["operations"] = {
        "status": "completed",
        "delivery_timeline": "90 days"
    }
    state["execution_order"].append("operations_agent")
    return state

# ==========================================
# WORKFLOW ORCHESTRATION
# ==========================================
workflow = StateGraph(GraphState) # type: ignore

# Register Nodes
workflow.add_node("legal", legal_node)
workflow.add_node("compliance", compliance_node)
workflow.add_node("finance", finance_node)
workflow.add_node("operations", operations_node)

# Define Execution Path
workflow.set_entry_point("legal")
workflow.add_edge("legal", "compliance")
workflow.add_edge("compliance", "finance")
workflow.add_edge("finance", "operations")
workflow.add_edge("operations", END)

app = workflow.compile()

# ==========================================
# REPORT GENERATION & MAIN EXECUTION
# ==========================================
def generate_analysis_report(final_state):
    print("\n" + "="*50)
    print("GENERATING CONTRACT ANALYSIS REPORT")
    print("="*50)

    report = {
        "timestamp": datetime.now().isoformat(),
        "query": final_state["query"],
        "execution_path": final_state["execution_order"],
        "results": {
            "legal": final_state.get("legal"),
            "finance": final_state.get("finance"),
            "compliance": final_state.get("compliance"),
            "operations": final_state.get("operations")
        }
    }

    filename = "contract_analysis_output.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=4)

    print(f"SUCCESS: Analysis completed. Report saved as '{filename}'")

if __name__ == "__main__":
    initial_input = {
        "query": "Review termination and payment terms.",
        "legal": {},
        "finance": {},
        "compliance": {},
        "operations": {},
        "execution_order": [],
        "memory": []
    }

    print("Starting Multi-Agent System...")

    try:
        final_result = app.invoke(initial_input) # type: ignore
        generate_analysis_report(final_result)
    except Exception as e:
        print(f"An error occurred during execution: {e}")