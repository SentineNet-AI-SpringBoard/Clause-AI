# ClauseAI – Multi-Agent Contract Analysis System

## Overview

ClauseAI is an AI-powered contract intelligence system designed to automatically interpret, analyze, and validate contractual clauses across multiple functional domains. The platform adopts a modular, multi-agent architecture where domain-specific agents collaborate to provide structured, explainable, and actionable insights from complex legal documents.

The system is orchestrated using LangGraph, enabling dynamic agent execution, shared state management, and inter-agent reasoning. This design ensures scalability, flexibility, and transparency throughout the contract analysis workflow.

---

## Key Capabilities

- Contract ingestion and preprocessing from PDF and TXT formats  
- Clause-level document segmentation with configurable overlap  
- Dense vector embedding generation for semantic understanding  
- Vector-based storage and similarity-based retrieval  
- Domain-specific analysis agents:
  - Legal
  - Compliance
  - Finance
  - Operations
- Rule-based and conditional agent routing  
- Multi-agent orchestration using LangGraph  
- Shared memory for agent-to-agent communication  
- Cross-domain validation and reasoning to enhance confidence and accuracy  

---

## Technology Stack

### Programming Language
- Python 3.10+

### Core Frameworks & Libraries
- **LangChain & LangGraph**  
  Used for agent orchestration, state management, and structured workflow execution  

- **Pinecone**  
  Vector database for semantic indexing and retrieval of clause embeddings  

- **NumPy & Pandas**  
  Data processing, transformation, and analysis  

- **Matplotlib**  
  Visualization and exploratory analysis  

- **Jupyter Notebook**  
  Experimentation, prototyping, and milestone-based development  

---

## Models Utilized

- Sentence-Transformer and Hugging Face models for embedding generation  
- Gemma-based language model for agent reasoning and response generation  

---

## Milestone 1: Foundational RAG Pipeline

The first milestone focused on setting up the development environment and implementing the foundational Retrieval-Augmented Generation (RAG) pipeline. This phase established the core workflow required for contract ingestion, semantic retrieval, and agent-based reasoning.

### Implemented Components

- Document ingestion and preprocessing  
- Clause chunking with overlap handling  
- Embedding generation and vector storage  
- Semantic retrieval for relevant clause selection  

### Challenges and Observations

- Initial embedding generation relied on API-based solutions before transitioning to a locally hosted sentence transformer model (`all-MiniLM-L6-v2`)  
- Multiple large language models, including Qwen 2.5 and Mistral-7B, were evaluated as base models  
- Due to hardware limitations (16 GB CPU RAM), larger models could not be reliably loaded in the local VS Code environment  
- A Gemma-based model was ultimately selected for its balance between computational efficiency and reasoning performance  

---

## Milestone 2: Multi-Agent Pipelines and Orchestration

The second milestone focused on evolving the system from a linear RAG pipeline to a coordinated, multi-agent architecture capable of structured reasoning across multiple domains. This phase introduced agent specialization, shared state management, and dynamic execution flows using LangGraph.

### Key Enhancements

- Design and implementation of domain-specific agents for Legal, Compliance, Finance, and Operations  
- Definition of agent responsibilities and scoped reasoning boundaries  
- Introduction of a shared state object to enable agent-to-agent communication  
- Construction of agent pipelines using LangGraph nodes and edges  
- Rule-based and conditional routing of agents based on document context and analysis outcomes  
- Support for sequential and parallel agent execution patterns  
- Cross-agent refinement logic to reconcile overlapping or conflicting insights  

### Orchestration with LangGraph

- LangGraph was used to model agents as graph nodes with well-defined inputs and outputs  
- Agent execution flow was controlled using conditional edges and runtime signals  
- The shared state enabled agents to reference prior analyses, reducing redundant computation  
- This orchestration approach improved modularity, debuggability, and extensibility of the system  

### Outcomes

- Transition from static, keyword-driven analysis to dynamic, context-aware reasoning  
- Improved consistency across domain analyses through shared memory  
- Enhanced scalability by enabling independent agent evolution  
- Strong foundation for future event-driven execution and user-interactive workflows  

---

## Future Scope

- Event-driven agent execution based on confidence thresholds and risk escalation  
- Persistent long-term memory for agents across multiple contracts  
- UI-driven contract exploration and follow-up querying  
- Explainability layers with evidence tracing and confidence scoring  
- Support for additional document formats and large-scale contract repositories  

---

## Summary

ClauseAI demonstrates a scalable and modular approach to contract intelligence by combining retrieval-augmented generation with coordinated multi-agent reasoning. Through structured pipelines and LangGraph-based orchestration, the system enables comprehensive, explainable, and extensible contract analysis workflows.
