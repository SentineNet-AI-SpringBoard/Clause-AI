ClauseAI: AI-Powered Contract Analysis System
1. Project Overview

ClauseAI is an intelligent contract analysis platform designed to streamline and automate contract review processes. The system enhances accuracy, reduces manual effort, and produces domain-specific, actionable insights through structured reports. It is built on a multi-agent AI framework, where each agent focuses on a specific analysis domain—such as Compliance, Finance, Legal, and Operations—to ensure a holistic and professional evaluation of contracts.

2. System Architecture and Methodology

ClauseAI follows a LangGraph-based architectural design, where each node represents a dedicated contract analysis function performed by a specialized agent.

2.1 Core Workflow

Input Stage
Users upload contract documents directly or integrate external legal data sources through APIs.

AI Planning Stage
A centralized Coordinator Agent determines the analysis flow and assigns responsibilities to relevant domain agents.

Analysis Stage
Domain-specific agents conduct in-depth evaluations using multi-turn reasoning with expert AI submodules. Data extraction and reasoning are executed in a parallelized manner for efficiency.

Reporting Stage
Outputs from all agents are aggregated and transformed into clear, concise, and professional contract analysis summaries.

3. Technology Stack

Programming Language: Python 3.x

Agent Orchestration: LangChain and LangGraph

Vector Database: Pinecone

Models: OpenAI API (for architectural design) and Gemma-2b-it (Milestone 1 implementation)

Document Parsing: PyPDF2, python-docx

Frontend Interface: Streamlit

4. Milestone 1 Implementation – Progress Summary

The first milestone focused on environment configuration and the successful deployment of a Retrieval-Augmented Generation (RAG) pipeline.

4.1 Data Pipeline Overview

Source Data
A collection of 510 text files stored in the full_contract_txt directory.

Processing Workflow
Documents were processed using LangChain, segmented into manageable chunks, and converted into embeddings stored within Pinecone.

Retrieval Setup
A total of 20 RAG search files were generated to provide contextual input for the specialized agents.

4.2 Challenges Encountered

Embedding generation initially relied on API keys for the sentence-transformer model (all-MiniLM-L6-v2).

Prior to finalizing Gemma-2b-it as the base model, alternatives such as Qwen2.5 and Mistral-7B were tested. However, due to their large model sizes, they failed to load in VS Code under a 16GB CPU RAM constraint.

5. Milestone 2 Implementation – Progress Summary

This milestone emphasized agent coordination, routing logic, and the construction of LangGraph nodes, enabling structured agent-to-agent communication.

5.1 Data Pipeline Overview

Source Data
Four pre-generated JSON output files corresponding to Legal, Compliance, Finance, and Operations agents, produced using the Gemma-2b-it model.

Processing Workflow

Agent outputs were treated as pre-computed data.

Routing rules and coordinator logic were implemented using keyword-based decision mechanisms.

LangGraph was initialized with all agents added as nodes, with the Legal Agent serving as the entry point.

Collaborative Agent Execution

The Compliance Agent identifies risks and records them in shared memory.

The Finance Agent references this memory to detect associated financial risks.

The Legal Agent performs final validation and consolidation.

5.2 Challenges Encountered

Initial agent outputs returned empty strings due to improper storage of pre-computed data.

No major issues were observed during the compilation and execution of the complete notebook after resolution.
