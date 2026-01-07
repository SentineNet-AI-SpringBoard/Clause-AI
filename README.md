**ClauseAI – Multi-Agent Contract Analysis System**

**Overview**
ClauseAI is a multi-agent contract analysis system designed to extract, validate, and analyze contractual clauses across multiple domains such as Legal, Compliance, Finance, and Operations. The system uses a modular, agent-based architecture orchestrated through LangGraph, enabling structured reasoning, inter-agent collaboration, and scalable analysis workflows.

**Key Features**
  1. Contract ingestion and preprocessing (PDF/TXT)
  2. Clause-level chunking with overlap
  3. Embedding generation and vector storage
  4. Semantic retrieval using vector search
  5. Domain-specific agents (Legal, Compliance, Finance, Operations)
  6. Rule-based and conditional agent routing
  7. Multi-agent orchestration using LangGraph
  8. Shared memory for agent-to-agent communication
  9. Cross-domain validation and reasoning

**Tech Stack**
**Programming Language**
Python 3.10+

**Core Frameworks & Libraries**
  1. LangGraph – Multi-agent orchestration and state management
  2. LangChain – Text splitting and pipeline utilities
  3. Sentence Transformers / Hugging Face – Embedding generation
  4. Pinecone – Vector database for semantic search
  5. gemma model – Agent reasoning
  6. NumPy, Pandas – Data handling
  7. Matplotlib – Visualizations
  8. Jupyter Notebook – Experimentation and milestone development

**Models Used**
1. Sentence-Transformer / Hugging Face embedding models
2. Gemma model for agents

**Milestone 1 Implementation**
The first milestone focused on environment setup and the establishment of the RAG (Retrieval-Augmented Generation) pipeline.

**Data Pipeline Details**
  1. Source Data: 510 text files from the full_contract_txt folder.
  2. Processing: Documents were transformed using LangChain, converted into chunks, and stored as embeddings in Pinecone.
  3. Retrieval: The system generated 20 RAG search files to serve as the context for specialized agents.

**Issues Faced:**
  1. Instead using API Key for embedding sentence transformer model - all-minilm-l6-v2
  2. Before using gemma-2b-it as the base model several other models like Qwen2.5, Mistral-7B where tried - but due the large size teh models failed to load in VSCode witha CPU memory of 16gb RAM
