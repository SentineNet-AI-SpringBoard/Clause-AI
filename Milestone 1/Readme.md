# ClauseAI – Contract Analysis Foundations

This document summarizes ClauseAI’s core components, including data preprocessing, semantic retrieval, and agent-based contract analysis with specialized agents.

## Data Ingestion & Preprocessing

Contracts are ingested from text-based sources (PDF, DOCX, TXT) and cleaned to remove headers, footers, page numbers, and formatting artifacts while preserving legal sentence structure, clause numbering, section headers, and references.

## Chunking Strategy

Contracts are split into semantically meaningful chunks for efficient retrieval.

* **Chunk size:** ~1000 characters
* **Overlap:** ~200 characters
* **Sentence-aware splitting** to avoid breaking clauses

Each chunk is stored with metadata including `chunk_id`, text, and source file.

## Embeddings & Semantic Retrieval

* **Model:** `all-MiniLM-L6-v2` (Sentence Transformers)
* Embeddings are generated locally and stored in a vector database
* Cosine similarity is used for retrieval

**Process:** Query → Embedding → Vector Search → Top-K Chunks → Agent Reasoning. Retrieved chunks are merged into a single context for agent processing.

## Retrieval-Augmented Generation (RAG)

* Agents never query the vector database directly
* Agents reason only on retrieved text
* Ensures grounding and traceability

## Agent Framework

* All agents use the `google/gemma-2b-it` model for instruction-tuned reasoning
* Agents differ only by prompts; execution logic is consistent
* Deterministic outputs with low temperature

### BaseAgent Responsibilities

* Accept RAG-retrieved context
* Construct strict prompts
* Invoke Gemma model
* Return structured JSON output

### Standard Output Schema

```json
{
  "clause_type": "",
  "extracted_clauses": [],
  "risk_level": "unknown",
  "confidence": 0.0,
  "evidence": []
}
```

## Implemented Agents

### Legal Agent

* Extracts termination clauses, governing law, and jurisdiction
* Focus: legal rights and enforceability

### Compliance Agent

* Extracts data protection obligations and regulatory clauses (GDPR, SOC2, ISO, HIPAA)

### Finance Agent

* Extracts payment terms, fees, penalties, and financial risk

### Operations Agent

* Extracts deliverables, timelines, SLAs, and milestones

## Grounding & Validation

* Outputs are verified against retrieved context
* Evidence is traceable to RAG chunks
* Ungrounded outputs are flagged or removed to prevent hallucinations
