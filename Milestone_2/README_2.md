# 🧠 Multi-Agent Contract Analysis System (Milestone 2)

## 📌 Project Overview
This project implements a **multi-agent contract analysis system** using **rule-based coordination**, **LangGraph-based orchestration**, **RAG-powered pipelines**, and a **final coordinator layer** to produce a unified legal, compliance, finance, and operations risk assessment.

Milestone 2 focuses on **agent orchestration, conditional routing, memory persistence, domain-specific pipelines, and coordinator-based output merging**.

---

## 🎯 Milestone 2 Objectives
- Build a rule-based **Coordinator**
- Introduce **LangGraph** for agent orchestration
- Support **conditional routing**
- Enable **agent memory & collaboration**
- Implement **domain-specific pipelines** (Legal, Compliance, Finance, Operations)
- Merge all outputs into a **final unified JSON response**

---

## 🧩 System Architecture (Milestone 2)

```

User Query
↓
Coordinator / LangGraph
↓
Relevant Agent(s)
↓
RAG Context → Analysis → Validation
↓
Pipeline Outputs (JSON)
↓
Final Coordinator Merge

````

---

## 🧠 Coordinator Logic (Rule-Based)

### Goals
- Route user queries to correct agents
- Collect structured agent outputs
- Act as the central orchestrator

### Routing Rules
```python
ROUTING_RULES = {
    "legal": ["termination", "governing law", "jurisdiction", "indemnity"],
    "compliance": ["gdpr", "audit", "regulatory", "data protection"],
    "finance": ["payment", "fee", "penalty", "invoice", "interest"],
    "operations": ["deliverable", "timeline", "sla", "milestone", "uptime"]
}
````

### Key Learnings

* **Coordinator ≠ Agent**
* Agents analyze domain data
* Coordinator routes, aggregates, and decides

---

## 🔗 LangGraph Basics

### Goals

* Understand nodes & edges
* Execute agents via graph
* Control execution order

### Features Implemented

* Shared `GraphState`
* Sequential execution
* Custom execution order (Compliance → Legal)
* Print logs to observe flow

---

## 🔄 Multi-Agent Graph (Nodes & Edges)

### Agents as Nodes

* `legal_agent`
* `compliance_agent`
* `finance_agent`
* `operations_agent`

### Capabilities

* Change execution order dynamically
* Remove agents and observe state changes
* Maintain shared state across agents

---

## 🔀 Conditional Routing in LangGraph

### Purpose

* Execute **only relevant agents**
* Avoid unnecessary computation

### Example

| Query                               | Agent Executed                       |
| ----------------------------------- | ------------------------------------ |
| "Review termination clause"         | Legal                                |
| "Check late payment penalties"      | Finance                              |
| "GDPR compliance and payment terms" | Compliance (single-entry limitation) |

---

## 🧠 Conversation Memory & Agent Collaboration

### Memory Features

* Persistent shared memory in graph state
* Agents write findings to memory
* Downstream agents read and validate earlier outputs

### Validation Examples

* Finance validates compliance penalties
* Legal validates finance exposure
* Operations validates SLA enforceability

---

## 📚 RAG-Based Domain Pipelines

All pipelines consume **real RAG-retrieved chunks** and do **not hallucinate results**.

---

### 🛡️ Compliance Pipeline

**Extracts:** GDPR, audits, regulatory obligations
**Steps:** Retrieval → Analysis → Validation → Risk Summary
**Enhancements:**

* Keyword tuning
* Confidence comparison
* Clause precision improvement

---

### 💰 Finance Pipeline

**Extracts:** Payment terms, penalties, interest
**Enhancements:**

* Added keyword: `interest`
* Observed increase in financial risk & confidence
* Penalty compounding identified

---

### ⚖️ Legal Pipeline

**Extracts:** Termination, liability, indemnification
**Enhancements:**

* Added keyword: `indemnification`
* Clause extraction bounded by RAG context
* High legal risk identification

---

### ⚙️ Operations Pipeline

**Extracts:** SLA, uptime, deliverables
**Observation:**

* Zero clauses when RAG context lacks operational data
* Demonstrates **non-hallucinating AI behavior**
* Validation flags missing obligations correctly

---

## 🧩 Coordinator: Merging Agent Outputs

### Responsibilities

* Merge all pipeline outputs
* Compute overall risk
* Aggregate confidence scores
* Identify highest-risk domain & clauses

### Final Output Includes

* Domain-wise analysis
* Overall risk level
* Overall confidence score
* Highest-risk clauses
* Timestamped JSON artifact

---

## 📦 Final Output (JSON)

```json
{
  "overall_risk": "High",
  "highest_risk_domain": "legal",
  "overall_confidence": 0.81,
  "highest_risk_clauses": [
    "Termination clause identified",
    "Limitation of liability clause identified"
  ]
}
```

---

## 🧠 Key Design Principles

* Separation of concerns (RAG vs Reasoning)
* Deterministic orchestration via LangGraph
* Memory-enabled multi-step reasoning
* Zero hallucination guarantee
* Modular, extensible pipelines

---

## 🚀 Technologies Used

* Python
* LangGraph
* JSON-based RAG outputs
* Rule-based coordination
* Modular agent architecture

---

## ✅ Milestone 2 Status

✔ Completed successfully
✔ All tasks implemented
✔ Outputs saved as JSON
✔ Ready for Milestone 3 (Parallel execution / API layer)