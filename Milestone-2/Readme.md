# Milestone 2 – Multi-Agent Contract Analysis with Memory

# Overview
This project implements a **multi-agent contract analysis system** using **LangGraph**.
Agents (Legal, Compliance, Finance, Operations) run **sequentially or in parallel**, persist their outputs in **shared state and vector memory**, and reuse stored intelligence for future analysis.

## Key Features
*  **Agent Memory & State Persistence**
*  **Agent-to-Agent Communication**
*  **Parallel Agent Execution (LangGraph)**
*  **Vector DB Storage & Recall**
*  **Coordinator for Risk Aggregation**
---
## Agents
* **Legal Agent** – Legal clause extraction & validation
* **Compliance Agent** – Regulatory & policy checks
* **Finance Agent** – Payment, penalties, interest risks
* **Operations Agent** – SLA, uptime, delivery obligations
---

## Tech Stack

* Python
* LangGraph
* RAG (Retrieval-Augmented Generation)
* Vector DB (e.g., Pinecone)
---

## How to Run
1. Install dependencies
2. Set environment variables (API keys, vector DB)
3. Run notebook:
   ```bash
   Milestone2_NewNotebook.ipynb
   ```
4. Execute:
   * Sequential pipelines
   * Parallel LangGraph execution
   * Memory storage & recall
   * Coordinator merge
---
## Memory & Vector Storage
Each agent output is stored with metadata:
* `agent`
* `contract_id`
* `timestamp`
* `risk_level`
Stored memories are **queried and reused** instead of re-running agents.

## Output
* Unified JSON contract analysis
* Cross-agent risk comparison
* Highest-risk clause identification

## Status
✅ Working prototype
🚀 Ready for extension (conflict resolution, contract comparison, dashboards)

