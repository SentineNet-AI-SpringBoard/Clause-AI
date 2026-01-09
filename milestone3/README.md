# Milestone 3 — Parallel Agents + Persistent Agent Memory (Pinecone)

## What was done
- Added sequential vs parallel execution (async) for multi-agent retrieval pipelines
- Persisted per-agent outputs into Pinecone as vector “agent memory” with metadata:
  - `contract_id`, `agent_type`, `timestamp`, `question`
- Implemented recall queries to fetch stored memory without rerunning agents
- Added notebook-side dependency repair helpers for common Windows/Anaconda issues

## Files
- Notebook: `Milestone3_ParallelAgents_PersistentMemory.ipynb`
- Outputs: `outputs/`
