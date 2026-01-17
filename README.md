# ClauseAI – Multi-Agent Contract Analysis System

 Overview

ClauseAI is an AI-powered contract intelligence system designed to analyze and validate contractual clauses across multiple domains using a **modular multi-agent architecture**. Domain-specific agents collaborate through a shared state to produce structured, explainable, and actionable insights from complex legal documents.

The system is orchestrated using **LangGraph**, enabling dynamic agent execution, inter-agent communication, and scalable workflow management.

---

## Key Capabilities
* Contract ingestion and preprocessing (PDF, TXT)
* Clause-level chunking with semantic embeddings
* Vector-based storage and similarity retrieval
* Domain-specific agents:

  * Legal
  * Compliance
  * Finance
  * Operations
* Multi-agent orchestration with shared memory
* Cross-domain validation and reasoning

---
---

## Models Used

* Sentence-Transformer / Hugging Face models for embeddings
* Gemma-based language model for agent reasoning

---
## Technology Stack
* **Language:** Python 3.10+
* **Frameworks:** LangChain, LangGraph
* **Vector DB:** Pinecone
* **Libraries:** NumPy, Pandas, Matplotlib
* **Environment:** Jupyter Notebook

## Milestone 1: Foundational RAG Pipeline
This phase focused on establishing the core Retrieval-Augmented Generation (RAG) workflow:

* Document ingestion and clause chunking
* Embedding generation and vector storage
* Semantic retrieval of relevant clauses

**Key Observation:**
Due to local hardware constraints, a Gemma-based model was selected for its balance of efficiency and reasoning quality.
---

## Milestone 2: Multi-Agent Orchestration
This milestone introduced coordinated, domain-specific reasoning using LangGraph:

* Specialized agents for Legal, Compliance, Finance, and Operations
* Shared state for agent-to-agent communication
* Sequential and parallel execution support
* Cross-agent validation to refine and reconcile findings

**Outcome:**
The system evolved from a linear pipeline to a scalable, context-aware multi-agent architecture.
---

## Future Scope
* Persistent long-term agent memory
* Event-driven and confidence-based execution
* UI-based contract exploration
* Explainability and evidence tracing
* Large-scale contract repository support
---

## Summary
ClauseAI combines **retrieval-augmented generation** with **multi-agent orchestration** to deliver scalable, explainable contract analysis. Its modular design and LangGraph-based execution provide a strong foundation for enterprise-grade contract intelligence systems.




