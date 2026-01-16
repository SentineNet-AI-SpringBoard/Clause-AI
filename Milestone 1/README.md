Milestone 1 - Documentation
1. Milestone Objective
    1. Environment setup with sentence transfomer all-minilm-l6-v2 and Pinecone vector database.
    2. Implement document upload and basic parsing of contract text.
    3. Define the role structure for AI analyst agents (Compliance, Finance, Legal, Operations).
    4. Conduct initial experiments on small sample contracts

2. Technical Implementation 
    1. Vector Database: Pinecone for efficient storage and retrieval of contract embeddings. 
    2. LLM: google/gemma-2b-it used for domain-specific clause extraction.
    3. Sentence Transformer - all-minilm-l6-v2
    4. Data Pipeline:
      1.  Input: Raw contract data (510 text files) was loaded from the full_contract_txt folder.
      2.  Processing: Text was transformed using LangChain and split into manageable chunks.
      3.  Vectorization: Chunks were converted into embeddings and stored in Pinecone.
      4.  Retrieval: The system generated 20 rag_search files to serve as context for the analysis agents.

3. Multi-Agent Analysis Results:
     In this milestone, four specialized agents processed the retrieved data and findings are given below:
      1. Compliance - Data protection, privacy, and regulatory obligations - High - 1.0
      2. Finance - Payment terms, billing, and out-of-pocket reimbursements - Medium - 0.7
      3. Operations - Deliverables, SLAs, and fulfillment responsibilities - Medium - 0.8
      4. Legal - IP rights, termination conditions, and governing law - Low - 0.85

4. Key Clause Extractions:
    1. Compliance: Strict non-disclosure requirements; confidential information cannot be shared with third parties without prior written consent.
    2. Finance: Recipients are obligated to reimburse providers including license fees and subcontractor payments.
    3. Operations: Specific entities are tasked with obtaining marketing licenses and handling product fulfillment.
    4. Legal: Defined events of default and requirements for written notice detailing the grounds for termination.
