ClauseAI: AI-Powered Contract Analysis

Milestone 1 – Progress Report
1. Project Overview
   
ClauseAI is an AI-powered system designed to automate contract analysis by improving efficiency and accuracy while generating structured, actionable insights. The system follows a multi-agent framework, where each AI agent specializes in a specific domain such as compliance, finance, and operations to provide comprehensive contract evaluation.

3. System Architecture & Methodology

ClauseAI is built using a LangGraph-based architecture, where each node represents a specialized contract analysis function.

2.1 Core Workflow

Input Phase
Users upload contract documents or provide access to external legal data sources.

AI Planning Phase
A Coordinator Agent analyzes the task and assigns responsibilities to domain-specific agents.

Analysis Phase
Specialized agents perform multi-turn reasoning and execute parallel data extraction using a Retrieval-Augmented Generation (RAG) approach.

Reporting Phase
Outputs from all agents are consolidated into concise and professional summaries.

3. Technology Stack

Programming Language: Python 3.x

Agent Orchestration: LangChain, LangGraph

Vector Database: Pinecone

Models Used:

OpenAI API (Architectural Design)

Gemma-2B-IT (Milestone 1 Implementation)

Document Parsing: PyPDF2, python-docx

Frontend: Streamlit

4. Milestone 1 Implementation Details

The first milestone focused on setting up the development environment and implementing the Retrieval-Augmented Generation (RAG) pipeline.

4.1 Data Pipeline

Source Data:

510 text files from the full_contract_txt directory

Processing:

Documents processed using LangChain

Text chunking applied for efficient embedding generation

Chunks converted into vector embeddings

Storage:

Generated embeddings stored in the Pinecone vector database

Retrieval:

20 RAG-based search context files created

These files serve as contextual input for specialized agent analysis

5. Issues Faced During Milestone 1

->Embedding Model Constraints
->Instead of local embedding generation, an API-based approach was used for the Sentence Transformer model (all-MiniLM-L6-v2) due to resource limitations.
->Large Model Memory Limitations
->Several large language models such as Qwen 2.5 and Mistral-7B were tested.
->These models failed to load locally due to CPU memory constraints (16 GB RAM) in VS Code.
->Model Selection Decision
->Gemma-2B-IT was selected as the base model for Milestone 1 due to its lower memory footprint and stable local performance.
