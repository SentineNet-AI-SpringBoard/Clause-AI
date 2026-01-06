CLAUSE AI — Milestone 1 Completion Report
Overview

CLAUSE AI is a contract intelligence system designed to analyze, retrieve, and assess legal agreements using Retrieval-Augmented Generation (RAG) and domain-specific AI agents.
Milestone 1 establishes the technical foundation, ensuring the system is accurate, grounded, scalable, and verifiable before introducing advanced orchestration, reasoning, or UI layers.

Objectives Achieved

Understand and validate the CUAD contract dataset

Perform exploratory data analysis (EDA) to assess data quality and distribution

Build a robust text preprocessing and chunking pipeline

Generate high-quality embeddings for semantic search

Integrate vector search using Pinecone

Implement a RAG-based retrieval layer

Design and validate a reusable agent framework

Develop domain-specific agents with grounded outputs

Dataset Understanding & EDA

A comprehensive exploratory data analysis was conducted to understand contract characteristics and dataset reliability.

Key analyses performed:

Distribution of contract sizes and text lengths

Word count per contract

Identification of frequently occurring legal terms

Detection of missing, empty, or malformed files

Visual analysis included:

Histogram of contract length

Boxplot of text length distribution

WordCloud of common legal clause keywords

Bar chart of top legal terms

Scatter plot of file size vs. word count

This step confirmed that the dataset is suitable for downstream chunking, embedding, and retrieval tasks.

Text Cleaning & Normalization

All preprocessing steps were formatting-only, ensuring that legal meaning and contractual intent were preserved.

Cleaning steps applied:

Removal of page headers and footers

Whitespace normalization

Removal of repeated line breaks

Removal of noisy characters (tabs, bullets, non-ASCII symbols)

Correction of hyphenation across line breaks
(e.g., “termi-nation” → “termination”)

Optional casing normalization while preserving original text when required

Preservation of legal section headers (e.g., TERMINATION, CONFIDENTIALITY)

Cleaned contracts were stored as transformed text files for traceability and auditability.

Sentence-Aware Chunking Strategy

To maximize retrieval accuracy and contextual integrity, a sentence-aware chunking strategy with overlap was implemented.

Configuration:

Chunk size: 1000 characters

Overlap: 200 characters

Sentence-boundary preservation

Validation performed:

Chunk length distribution analysis

Overlap consistency checks

This approach minimizes context loss during retrieval and improves downstream agent accuracy.

Embedding Generation

Semantic embeddings were generated using:

Model: all-MiniLM-L6-v2 (Sentence Transformers)

Rationale:

High-quality semantic representations

Lightweight and fast

Efficient for vector databases

Strong performance in semantic search tasks

Cost-effective and scalable

Quality checks performed:

Vector dimensionality validation

Embedding norm distribution visualization

Similarity sanity checks using cosine similarity and dot product

Embeddings were stored in structured JSON format for reproducibility.

Vector Search & Pinecone Integration

A Pinecone vector index was created and populated with contract embeddings.

Capabilities validated:

Semantic search over legal text

Top-K similarity retrieval

Similarity score distribution analysis

Query relevance verification

This layer serves as the retrieval backbone for all agents.

Retrieval-Augmented Generation (RAG)

A RAG wrapper was implemented to ensure fact-grounded and verifiable outputs.

RAG workflow:

User query is embedded

Top-K relevant chunks are retrieved from Pinecone

Retrieved text is passed as context to agents

Similarity scores are recorded

Retrieved evidence is stored for auditability

Agent Framework Design

A reusable agent framework was designed to standardize agent behavior and enforce output validation.

Core features:

Common output schema

BaseAgent abstraction

JSON schema validation

Grounding and cross-verification against RAG context

All agent responses are validated before being consumed downstream.

Domain-Specific Agents Implemented

Each agent operates strictly on RAG-retrieved context and produces structured, verifiable JSON outputs.

Legal Agent

Extracts termination, jurisdiction, and governing law clauses

Assesses legal risk levels

Compliance Agent

Identifies regulatory and policy obligations

Covers GDPR, SOC2, ISO, and HIPAA references

Assesses compliance risk

Finance Agent

Extracts payment terms, fees, penalties, and liabilities

Assesses financial risk exposure

Operations Agent

Identifies deliverables, timelines, milestones, and SLAs

Assesses operational and execution risk

Language Model Used

LLM: gemma-2b-it

Rationale:

Lightweight and instruction-tuned

Cost-effective for experimentation

Low-latency inference

Adequate reasoning capability for structured extraction

Suitable for multi-agent pipelines in early stages

Grounding & Verification Guarantees

All generated JSON outputs are fully grounded in RAG-retrieved contract text

No hallucinated clauses or assumptions

Every extracted clause is backed by explicit evidence

All outputs are cross-verified against retrieved chunks

Results are auditable, explainable, and reproducible

Milestone 1 Status

✅ Dataset understanding & EDA completed
✅ Cleaning, chunking, and embeddings validated
✅ Vector search & RAG operational
✅ Agent framework implemented
✅ Legal, Compliance, Finance, and Operations agents completed

Milestone 1 successfully establishes a reliable and grounded foundation for advanced agent orchestration and contract intelligence in subsequent milestones.