import os
from typing import TypedDict, List

# --- 1. STATE DEFINITION ---
class AgentState(TypedDict):
    task: str
    results: List[str]
    signals: dict
    memory_checked: bool

# --- 2. THE AGENT TOOLS ---
def legal_agent(state: AgentState):
    print("⚖️ [Legal Agent]: Analyzing liability and risk...")
    return {
        "results": ["Found high-risk indemnity clause in Section 4."], 
        "signals": {"risk": "high"}
    }

def finance_agent(state: AgentState):
    print("💰 [Finance Agent]: Checking payment terms and penalties...")
    return {
        "results": ["Payment terms are Net-30 with 2% late fee."], 
        "signals": {"risk": "low"}
    }

def pinecone_memory_check(task: str):
    # Simulating a search in Pinecone Vector DB
    print("🔍 [Memory]: Checking Pinecone for existing analysis...")
    return False # Set to True to see how the Controller skips work

# --- 3. THE DYNAMIC CONTROLLER (The "Brain") ---
def controller(state: AgentState):
    print("\n🤖 [Controller]: Evaluating live signals...")
    
    # Check 1: Memory Signal (Run only once at the start)
    if not state['memory_checked']:
        state['memory_checked'] = True
        if pinecone_memory_check(state['task']):
            print("✨ [Controller]: Memory found! Ending process.")
            return "end"
    
    # Check 2: Event-Driven Trigger (If risk is high, we might need a specific action)
    if state['signals'].get('risk') == 'high' and "Legal" not in str(state['results']):
        return "legal_agent"

    # Check 3: Logic Routing based on keywords if no results exist yet
    if len(state['results']) == 0:
        if "pay" in state['task'].lower() or "price" in state['task'].lower():
            return "finance_agent"
        else:
            return "legal_agent"
    
    # Check 4: Termination
    print("✅ [Controller]: All necessary agents have reported. Ending.")
    return "end"

# --- 4. THE EXECUTION ENGINE ---
def run_clause_ai(user_query: str):
    # Initialize the Live State
    state: AgentState = {
        "task": user_query,
        "results": [],
        "signals": {},
        "memory_checked": False
    }

    # Start the loop
    next_step = controller(state)
    
    max_iterations = 5
    count = 0
    
    while next_step != "end" and count < max_iterations:
        if next_step == "legal_agent":
            output = legal_agent(state)
        elif next_step == "finance_agent":
            output = finance_agent(state)
        
        # Update the live state with new findings
        state['results'].extend(output['results'])
        state['signals'].update(output['signals'])
        
        # Ask the Controller what to do next based on NEW signals
        next_step = controller(state)
        count += 1

    print("\n--- FINAL SYSTEM REPORT ---")
    for i, res in enumerate(state['results'], 1):
        print(f"{i}. {res}")

# --- START ---
if __name__ == "__main__":
    print("--- STARTING LIVE AGENTIC SYSTEM ---")
    # Test Query
    query = "Please analyze the payment terms of this contract."
    run_clause_ai(query)
