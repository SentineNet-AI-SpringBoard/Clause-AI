# ClauseAI -- Contract Analysis Foundations

This document describes the completed components of ClauseAI covering
data preprocessing, semantic retrieval, and agent-based contract
analysis, up to the definition and execution of specialized agents.

------------------------------------------------------------------------

## Data Ingestion & Preprocessing

Legal contracts are ingested from raw text-based sources (PDF, DOCX, or
TXT after extraction).

### Text Cleaning

The following preprocessing steps are applied:

-   Removal of headers, footers, page numbers, and formatting artifacts\
-   Normalization of whitespace and line breaks\
-   Preservation of legal sentence structure and clause numbering\
-   Retention of section headers and legal references

The primary objective of cleaning is to remove noise without altering
legal meaning.

------------------------------------------------------------------------

## Chunking Strategy

Contracts are split into semantically meaningful chunks to enable
efficient retrieval.

### Configuration

-   **Chunk size:** \~1000 characters\
-   **Overlap:** \~200 characters\
-   **Sentence-aware splitting** to avoid breaking legal clauses

Overlapping chunks ensure that important legal context is preserved
across boundaries.

Each chunk is stored with metadata:

``` json
{
  "chunk_id": 12,
  "text": "Either party may terminate this Agreement upon thirty (30) days written notice...",
  "source_file": "contract_001.txt"
}
```

------------------------------------------------------------------------

## Embeddings & Semantic Retrieval

### Embedding Model

Semantic embeddings are generated using Sentence Transformers.

-   **Model:** `all-MiniLM-L6-v2`\
-   Lightweight, fast, and open-source\
-   Well-suited for semantic similarity on legal text

**Design separation:**

-   Sentence Transformers are used strictly for retrieval\
-   Language models are used only for reasoning

### Vector Storage & Search

-   Embeddings are generated locally\
-   Stored in a vector database using cosine similarity

Metadata stored alongside vectors:

-   filename\
-   chunk_id\
-   chunk text

For each query:

1.  Query is embedded\
2.  Top-K relevant chunks are retrieved\
3.  Retrieved chunks are merged into a single context

Retrieved results are stored as structured JSON files and act as the
only source of truth for agent reasoning.

------------------------------------------------------------------------

## Retrieval-Augmented Generation (RAG)

The system follows a strict RAG pattern:

-   Agents never query the vector database directly\
-   Agents reason only on retrieved text\
-   Grounding and traceability are guaranteed

**RAG flow:**

    Query → Embedding → Vector Search → Top-K Chunks → Agent Reasoning

------------------------------------------------------------------------

## Agent Framework

The intelligence layer is implemented using multiple specialized agents
built on a common base architecture.

### Language Model for Agents

All agents use the Gemma instruction-tuned model.

-   **Model:** `google/gemma-2b-it`\
-   Instruction-following\
-   Lightweight and open-source\
-   Suitable for structured JSON generation

Gemma is used exclusively for reasoning on retrieved context.

------------------------------------------------------------------------

## BaseAgent Design

A reusable `BaseAgent` class is implemented.

### Responsibilities

-   Accept RAG-retrieved contract context\
-   Construct strict prompts\
-   Invoke the Gemma model\
-   Return raw structured output

Agents differ only by their prompts; execution logic remains identical.

-   Deterministic generation enforced\
-   Low temperature\
-   No sampling

------------------------------------------------------------------------

## Standard Agent Output Schema

All agents produce output in a uniform JSON format:

``` json
{
  "clause_type": "",
  "extracted_clauses": [],
  "risk_level": "unknown",
  "confidence": 0.0,
  "evidence": []
}
```

This schema ensures:

-   Machine-readability\
-   Consistent validation\
-   Safe downstream processing\
-   Reduced hallucination risk

------------------------------------------------------------------------

## Implemented Agents

### Legal Agent

Extracts:

-   Termination clauses\
-   Governing law\
-   Jurisdiction

**Focus:** Legal rights, remedies, and enforceability.

------------------------------------------------------------------------

### Compliance Agent

Extracts:

-   Data protection obligations\
-   Regulatory and audit clauses

**Keyword grounding includes:**

-   GDPR\
-   SOC2\
-   ISO\
-   HIPAA

------------------------------------------------------------------------

### Finance Agent

Extracts:

-   Payment terms\
-   Fees and invoices\
-   Penalties and late fees

**Focus:** Financial exposure and monetary risk.

------------------------------------------------------------------------

### Operations Agent

Extracts:

-   Deliverables\
-   Timelines\
-   Service Level Agreements (SLAs)\
-   Milestones

**Focus:** Operational execution and performance obligations.

------------------------------------------------------------------------

## Grounding & Validation

A grounding layer ensures trustworthiness of agent outputs:

-   Extracted clauses must exist verbatim in retrieved context\
-   Evidence must be traceable to RAG chunks\
-   Ungrounded outputs are flagged or removed

This prevents hallucinated or unsupported legal statements.
