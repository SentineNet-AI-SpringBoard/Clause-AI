import os
from typing import TypedDict, List, Optional

# --- 1. STATE DEFINITION ---
# This keeps track of everything happening in the "live" session
class AgentState(TypedDict):
    task: str
    plan: List[str]
    current_agent: str
    results: List[str]
    signals: dict  # Dynamic signals: {'risk': 'high', 'confidence': 0.5}
    memory_found: bool

# --- 2. THE AGENT TOOLS ---
def legal_agent(state: AgentState):
    print("⚖️ [Legal Agent]: Analyzing liability and risk...")
    # Simulate finding a high risk
    return {"results": ["Found high-risk indemnity clause."], "signals": {"risk": "high"}}

def finance_agent(state: AgentState):
    print("💰 [Finance Agent]: Checking payment terms and penalties...")
    return {"results": ["Payment terms are Net-30."], "signals": {"risk": "low"}}

def pinecone_memory_check(task: str):
    # This is where you'd connect to Pinecone. 
    # For now, it returns False to simulate "No previous memory found."
    print("🔍 [Memory]: Checking Pinecone for existing analysis...")
    return False 

# --- 3. THE DYNAMIC CONTROLLER (The "Brain") ---
def controller(state: AgentState):
    print("\n🤖 [Controller]: Evaluating live signals...")
    
    # Check 1: Memory Signal
    if state.get("memory_found") is None:
        exists = pinecone_memory_check(state['task'])
        if exists:
            print("✨ [Controller]: Memory found! Skipping to END.")
            return "end"
    
    # Check 2: Risk Signal (Event-Driven)
    if state['signals'].get('risk') == 'high':
        print("⚠️ [Controller]: High risk detected! Routing to Legal Expert.")
        return "legal_agent"

    # Check 3: Logic Routing
    if "price" in state['task'].lower() or "pay" in state['task'].lower():
        return "finance_agent"
    
    return "legal_agent"

# --- 4. THE EXECUTION LOOP (Simulating the Live System) ---
def run_dynamic_system(user_query: str):
    # Initialize State
    state: AgentState = {
        "task": user_query,
        "results": [],
        "signals": {},
        "memory_found": False,
        "current_agent": ""
    }

    # Step 1: Controller decides first move
    next_step = controller(state)
    
    # Step 2: Loop until finished
    limit = 0
    while next_step != "end" and limit < 3:
        if next_step == "legal_agent":
            output = legal_agent(state)
        elif next_step == "finance_agent":
            output = finance_agent(state)
        
        # Update State with Agent findings
        state['results'].extend(output.get("results", []))
        state['signals'].update(output.get("signals", {}))
        
        # Controller decides next move based on NEW signals
        next_step = controller(state)
        
        # Safety break to avoid infinite loops
        if "High-risk" in str(state['results']):
            next_step = "end" 
        limit += 1

    print("\n✅ Final Analysis Result:", state['results'])

# --- START THE SYSTEM ---
if __name__ == "__main__":
    print("--- STARTING LIVE AGENTIC SYSTEM ---")
    query = "Analyze the payment and liability clauses in this contract."
    run_dynamic_system(query)
