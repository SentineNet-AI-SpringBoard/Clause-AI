#### CLAUSE AI – Milestone 1
----
Contract Intelligence System for Legal Document Analysis using NLP, RAG, and Multi-Agent Architecture.

----

#### Project Objective
----
Build a clean, scalable foundation for contract analysis by preparing data, generating embeddings, enabling semantic search, and creating a reusable agent framework for legal reasoning.

----

#### Dataset Understanding & EDA
----
- Analyzed contract size and length distribution  
- Counted words per contract  
- Identified frequent legal terms  
- Detected missing or empty contract files  

**Visualizations included:**  
- Histogram (contract length)  
- Boxplot (text length distribution)  
- Wordcloud (common clause keywords)  
- Bar chart (top 20 legal terms)  
- Scatter plot (file size vs word count)  

Notebook:  
`notebooks/Milestone1_ProjectPlanning_Setup_EDA.ipynb`

----

#### Project Structure & Environment Setup
----
- Created main project folder: `CLAUSE_AI`  
- Subfolders: `artifacts`, `data`, `app`, `notebooks`, `env`  
- Data subfolders: `raw`, `transformed`  
- Python virtual environment setup using `venv`  
- Dependency management via `requirements.txt`

----

#### Text Cleaning & Normalization
----
- Removed headers, footers, and noisy characters  
- Normalized whitespace and line breaks  
- Fixed broken hyphenation (e.g., `termi\nnation → termination`)  
- Preserved legal section headers and structure  
- Ensured formatting changes only (no semantic loss)  

Output:  
`data/transformed/{contract_id}_cleaned.txt`

----

#### Sentence-Aware Chunking with Overlap
----
- Chunk size: **1000 characters**  
- Overlap: **200 characters**  
- Maintained sentence and paragraph boundaries  
- Generated chunk files for all contracts  

Output:  
`data/chunks/contract_XXX_chunks.json`

----

#### Embedding Generation & Validation
----
- Generated embeddings for each chunk  
- Stored vectors locally in JSON format  
- Validated embedding dimensions  
- Visualized embedding norm distribution  
- Performed cosine similarity & dot-product checks  

Model: `text-embedding-3-small`

----

#### Pinecone Vector Indexing & Semantic Search
----
- Initialized Pinecone client  
- Created / connected to `cuad-index`  
- Upserted embeddings (first 20 contracts)  
- Tested semantic search queries  
- Visualized top-K similarity scores  

----

#### Retrieval-Augmented Generation (RAG) Wrapper
----
- Embedded user queries  
- Retrieved top-K relevant contract chunks  
- Highlighted matching legal text  
- Saved retrieval results as JSON  

Purpose: Shared retrieval layer for all agents

----

#### Agent Framework Setup
----
- Defined a standard agent output schema  
- Built reusable `BaseAgent` class  
- Enforced strict JSON validation  
- Ensured safe and consistent agent outputs  

----

#### Legal Agent
----
- Extracted legal clauses (Termination, Governing Law, Jurisdiction)  
- Assessed legal risk levels  
- Returned structured legal analysis  

----

#### Compliance Agent
----
- Identified regulatory & compliance clauses  
- Assessed compliance risk  
- Student task: Extend prompts with GDPR, SOC2, ISO, HIPAA  

----

#### Finance Agent
----
- Extracted payment, penalty, and liability clauses  
- Assessed financial risk  
- Student task: Include late fees & penalty keywords  

----

#### Operations Agent
----
- Identified deliverables, timelines, and SLAs  
- Assessed execution risk  
- Student task: Include timeline & milestone keywords  

----

#### Milestone-1 Summary
----
- Established a clean legal data pipeline  
- Enabled scalable semantic retrieval using Pinecone  
- Built a reusable RAG framework  
- Created a standardized multi-agent foundation  
- Prepared the system for advanced reasoning and orchestration  

----
