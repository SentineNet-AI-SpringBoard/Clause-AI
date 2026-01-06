ClauseAI: AI-Powered Legal Contract Analysis

1. Project Overview
    ClauseAI is an AI-powered system designed to automate the process of contract analysis, improving efficiency and precision while generating customized, actionable reports. It leverages a multi-agent framework where each AI agent specializes in a distinct domain—such as compliance, finance, and operations—to deliver comprehensive and professional insights.

2. System Architecture & Methodology
    The system employs a LangGraph architecture, where each node represents a specialized contract analysis function.
    1. Core Workflow
      1. Input Phase: Users upload contract documents or connect to external legal data APIs.
      2. AI Planning Phase: A Coordinator agent assigns tasks to specialized domain agents.
      3. Analysis Phase: Domain agents perform multi-turn discussions with expert AI submodules and execute parallelized data extraction.
      4. Reporting Phase: The system synthesizes multi-agent outputs into concise, professional summaries.

3. Technology Stack
    1. Programming Language: Python 3.x 
    2. Orchestration: LangChain & LangGraph 
    3. Vector Database: Pinecone 
    4. Models: OpenAI API (Architecture) and Gemma-2b-it (Milestone 1 Implementation) 
    5. Parsing: PyPDF2, python-docx 
    6. Frontend: Streamlit

4. Milestone 1 Implementation: Progress Report
    The first milestone focused on environment setup and the establishment of the RAG (Retrieval-Augmented Generation) pipeline.
    1. Data Pipeline Details
      1. Source Data: 510 text files from the full_contract_txt folder.
      2. Processing: Documents were transformed using LangChain, converted into chunks, and stored as embeddings in Pinecone.
      3. Retrieval: The system generated 20 RAG search files to serve as the context for specialized agents.
   2. Issues Faced:
      1. Instead using API Key for embedding sentence transformer model - all-minilm-l6-v2
      2. Before using gemma-2b-it as teh base model several other models like Qwen2.5, Mistral-7B where tried - but due the large size teh models failed to load in VSCode witha CPU memory of 16gb RAM
