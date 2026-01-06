Milestone 1 - Documentation

Milestone Objective

Environment setup with sentence transfomer all-minilm-l6-v2 and Pinecone vector database.
Implement document upload and basic parsing of contract text.
Define the role structure for AI analyst agents (Compliance, Finance, Legal, Operations).
Conduct initial experiments on small sample contracts
Technical Implementation

Vector Database: Pinecone for efficient storage and retrieval of contract embeddings.
LLM: google/gemma-2b-it used for domain-specific clause extraction.
Sentence Transformer - all-minilm-l6-v2
Data Pipeline:
Input: Raw contract data (510 text files) was loaded from the full_contract_txt folder.
Processing: Text was transformed using LangChain and split into manageable chunks.
Vectorization: Chunks were converted into embeddings and stored in Pinecone.
Retrieval: The system generated 20 rag_search files to serve as context for the analysis agents.
Multi-Agent Analysis Results: In this milestone, four specialized agents processed the retrieved data and findings are given below:

Compliance - Data protection, privacy, and regulatory obligations - High - 1.0
Finance - Payment terms, billing, and out-of-pocket reimbursements - Medium - 0.7
Operations - Deliverables, SLAs, and fulfillment responsibilities - Medium - 0.8
Legal - IP rights, termination conditions, and governing law - Low - 0.85
Key Clause Extractions:

Compliance: Strict non-disclosure requirements; confidential information cannot be shared with third parties without prior written consent.
Finance: Recipients are obligated to reimburse providers including license fees and subcontractor payments.
Operations: Specific entities are tasked with obtaining marketing licenses and handling product fulfillment.
Legal: Defined events of default and requirements for written notice detailing the grounds for termination.
