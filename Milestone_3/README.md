# CLAUSE AI — Milestone 3

## Objective
Milestone 3 exposes the ClauseAI multi-agent system as a real-time API and UI-ready service using FastAPI and Swagger.

## What was built
- FastAPI backend for ClauseAI
- `/analyze` endpoint for contract upload
- Swagger UI for testing
- Dynamic RAG retrieval using Pinecone
- Multi-agent execution (Legal, Compliance, Finance, Operations)
- Coordinator layer to merge agent outputs
- Overall risk scoring logic
- JSON response for frontend/UI

## Data Source
All agents use:
- CUAD contracts
- Pinecone vector search
- SentenceTransformer embeddings
- RAG-retrieved contract chunks

No static or dummy outputs are used.

## Output
A live contract-risk JSON including:
- Extracted clauses
- Evidence
- Risk levels
- Confidence scores
- Overall contract risk
- Timestamp

## Status
Milestone-3 fully completed and API ready.
