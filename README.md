# ClauseAI – Multi-Agent Contract Analysis System

## Overview

ClauseAI is an AI-driven platform for automated contract analysis, designed to extract, validate, and interpret clauses across Legal, Compliance, Finance, and Operations domains. It uses a modular, multi-agent architecture with LangGraph for orchestrating agents, shared state management, and inter-agent reasoning, ensuring scalable, transparent, and explainable insights.

## Key Capabilities

* Contract ingestion and preprocessing from PDF and TXT files
* Clause-level segmentation with configurable overlap
* Dense vector embeddings for semantic understanding
* Vector-based storage and similarity search
* Domain-specific agents: Legal, Compliance, Finance, Operations
* Rule-based and conditional agent routing
* Multi-agent orchestration using LangGraph
* Shared memory for inter-agent communication
* Cross-domain validation to improve accuracy and confidence

## Technology Stack

* **Python 3.10+**
* **LangChain & LangGraph:** Agent orchestration and structured workflow
* **Pinecone:** Vector database for clause embeddings
* **NumPy & Pandas:** Data processing and analysis
* **Matplotlib:** Visualizations
* **Jupyter Notebook:** Experimentation and prototyping

## Models

* Sentence-Transformer and Hugging Face models for embeddings
* Gemma-based model for agent reasoning

## Milestone 1 – Foundational RAG Pipeline

Established core workflow for contract ingestion, semantic retrieval, and agent reasoning.

* Document ingestion and preprocessing
* Clause chunking with overlap
* Embedding generation and vector storage
* Retrieval of relevant clauses

**Challenges:**

* API-based embedding replaced with local `all-MiniLM-L6-v2` model
* Evaluated larger models (Qwen 2.5, Mistral-7B) but limited RAM (16GB) prevented loading
* Selected Gemma model for efficiency and reasoning performance

## Milestone 2 – Multi-Agent Orchestration

Transitioned from linear RAG to coordinated multi-agent system.

* Domain-specific agents for Legal, Compliance, Finance, Operations
* Shared state for inter-agent communication
* Agent pipelines modeled with LangGraph nodes and edges
* Rule-based and conditional agent execution
* Sequential and parallel execution patterns
* Cross-agent refinement for overlapping insights

**Outcomes:**

* Context-aware reasoning replacing keyword-based analysis
* Consistent domain analyses via shared memory
* Modular and extensible architecture supporting future growth

## Milestone 3 – Advanced Reasoning and Validation

Focused on enhancing agent intelligence with cross-domain validation, structured output schemas, and explainable reasoning.

* Implementation of advanced validation logic for clause extraction
* Standardized output schemas for all agents ensuring consistency
* Cross-agent reasoning to reconcile conflicting or overlapping insights
* Enhanced evidence tracing and confidence scoring
* Integration of operational workflows for end-to-end automated analysis

**Outcomes:**

* Improved accuracy and reliability of agent outputs
* Transparent, traceable reasoning across multiple domains
* Strong foundation for enterprise-grade deployment and interactive contract exploration
* Reduced risk of hallucinations or unsupported conclusions

## Milestone 4 – End-to-End UI Integration and System Deployment

Milestone 4 focused on transforming ClauseAI into a fully usable end-to-end application by integrating the multi-agent backend with an interactive Streamlit-based user interface. This milestone enabled authenticated access, persistent analysis tracking, and seamless user interaction with the underlying multi-agent intelligence.

* Streamlit-based UI for contract upload and analysis
* FastAPI backend integration for analysis and authentication
* Secure user login and session management
* Persistent storage of analysis inputs and outputs
* History management for previously executed analyses
* Stateless frontend with backend-managed state and data

**Outcomes:**

* Complete end-to-end workflow from document upload to multi-agent insights
* Improved usability and accessibility for non-technical users
* Reliable persistence and traceability of analysis results
* Clear separation of concerns between UI, backend, and agent logic
* Readiness for real-world usage and deployment

## Summary

ClauseAI combines retrieval-augmented generation with multi-agent orchestration and a user-facing interface to deliver scalable, explainable, and extensible contract intelligence. The system enables automated, cross-domain, and reliable contract analysis workflows suitable for practical and enterprise use.

