# CLAUSE AI — Milestone 2

## Objective
Milestone 2 implements multi-agent orchestration using LangGraph, dynamic routing, agent memory, pipelines, and final coordination.

## What was built
- LangGraph based agent execution
- Conditional routing (Legal, Compliance, Finance, Operations)
- Agent memory and cross-agent validation
- Compliance, Finance, Legal, Operations pipelines
- Coordinator to merge all agent outputs
- Grounding and hallucination control via RAG

## Data Source
All agents use:
- CUAD contracts
- Pinecone vector search
- RAG-retrieved legal text

No dummy data is used.

## Output
A unified contract-risk JSON including:
- Extracted clauses
- Evidence
- Risk levels
- Cross-agent validation
- Overall contract risk

## Status
Milestone-2 fully completed and validated.
