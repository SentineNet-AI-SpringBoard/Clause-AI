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

## Backend (FastAPI)
- Backend code: `backend/`
- Run locally:
  - `pip install -r requirements.txt`
  - `cd milestone3/backend`
  - `uvicorn app:app --reload --port 8000`

## Backend additions (SQLite auth + history)
Milestone 3 backend now also includes a small SQLite database to persist:
- Users + sessions (token-based)
- Per-user analysis history (Ask + Launch Analysis runs)

## Tests
- Run: `pytest -q`
