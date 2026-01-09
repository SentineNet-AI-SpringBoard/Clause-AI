# Clause-AI — Milestone Deliverables (Vinod)

This repository contains milestone-based deliverables for a contract analysis project built around:
- RAG (Retrieval-Augmented Generation) style retrieval over contract text using a vector database (Pinecone)
- A multi-agent pattern (legal / compliance / finance / operations)
- Persistent “agent memory” stored as vectors (so follow-up questions can reuse past agent results)

The work is organized into milestone folders with:
- the notebook for that milestone
- an `outputs/` folder containing the saved artifacts produced by running the notebook

---

## Repository structure

The main deliverables are:

- `milestone1/`
   - `Milestone1_ProjectPlanning_Setup_EDA.ipynb`
   - `outputs/`
- `milestone2/`
   - `Milestone2_Pinecone_VectorDB.ipynb`
   - `outputs/` (RAG results, agent outputs, search outputs)
- `milestone3/`
   - `Milestone3_ParallelAgents_PersistentMemory.ipynb`
   - `outputs/` (Milestone 3 run artifacts)

Large raw datasets and model caches are intentionally excluded from git via `.gitignore`.

---

## RAG architecture (how the system works)

RAG = Retrieval-Augmented Generation. In this project, the “generation” step can be a structured agent output, and retrieval is done via Pinecone.

### 1) Offline / ingestion stage (Milestone 2)
1. Load contract documents / text.
2. Split text into smaller chunks (passages).
3. Create vector embeddings for each chunk.
4. Upsert `{id, vector, metadata}` into Pinecone.

Typical metadata includes fields like `contract_id`, source filename, page number, chunk index, etc.

### 2) Online / query stage (Milestone 2 + 3)
1. User question is embedded into a query vector.
2. Pinecone retrieves top matching chunks (`top_k` most similar vectors).
3. The pipeline collects the retrieved context and returns results.

### 3) Multi-agent pattern (Milestone 3)
Instead of a single retrieval query, the system runs multiple specialized pipelines (“agents”):
- `legal_agent`: termination, breach, confidentiality, indemnification
- `compliance_agent`: privacy, regulatory, audit, retention, incident reporting
- `finance_agent`: fees, invoices, penalties, interest, liability/indemnity
- `operations_agent`: deliverables, milestones, SLAs, performance, uptime/service credits

Each agent issues a small set of domain-specific retrieval queries and aggregates the retrieved matches.

### 4) Persistent agent memory (Milestone 3)
After agents run, their outputs are embedded and stored back into Pinecone in a separate namespace (e.g., `agent_memory`).

Each memory record stores metadata:
- `contract_id`
- `agent_type`
- `timestamp`
- `question`

Later, you can query Pinecone to recall relevant stored agent outputs without rerunning the agents.

---

## Milestone 1 — Project Planning / Setup / EDA

Notebook:
- `milestone1/Milestone1_ProjectPlanning_Setup_EDA.ipynb`

What was done:
- Project setup and initial exploration of the CUAD contract dataset
- Basic EDA to understand dataset shape and distributions
- Created summary outputs used for later milestones

Outputs:
- Saved under `milestone1/outputs/`

---

## Milestone 2 — Pinecone VectorDB + Retrieval

Notebook:
- `milestone2/Milestone2_Pinecone_VectorDB.ipynb`

What was done:
- Prepared contract text for retrieval (chunking)
- Generated embeddings for chunks
- Indexed vectors into Pinecone
- Ran retrieval queries and stored RAG-style outputs

Outputs:
- Agent pipeline outputs and retrieval artifacts are saved under `milestone2/outputs/`
- `milestone2/outputs/rag_results/` contains saved retrieval results per question

---

## Milestone 3 — Parallel Agents + Persistent Agent Memory (Pinecone)

Notebook:
- `milestone3/Milestone3_ParallelAgents_PersistentMemory.ipynb`

What was done:
- Implemented sequential vs parallel execution of agent pipelines (async fan-out)
- Added timing comparison (sequential runtime vs parallel runtime)
- Persisted per-agent outputs into Pinecone as vector “agent memory” records
- Implemented recall queries that fetch stored agent memory by `contract_id` and optionally `agent_type`

Windows / Anaconda robustness:
- Added a notebook cell to repair dependency mismatches (`huggingface-hub`, `transformers`, `sentence-transformers`)
- Added guards to avoid optional TensorFlow imports that commonly fail with DLL errors

Outputs:
- Saved under `milestone3/outputs/`

---

## How to run (reproducible steps)

### 1) Create environment + install requirements
From repo root:

1. `pip install -r requirements.txt`

If you use conda, create/activate your conda env first, then run the same pip install.

### 2) Configure Pinecone credentials
Recommended: create a `.env` file in repo root:

```
PINECONE_API_KEY=YOUR_KEY_HERE
PINECONE_INDEX=cuad-index
```

Notes:
- `.env` is ignored by git (secrets are not committed).
- The Milestone 3 notebook auto-loads `.env` (without requiring extra packages).

### 3) Run notebooks
Run in order if starting from scratch:
1. Milestone 1 notebook
2. Milestone 2 notebook (build/index vectors)
3. Milestone 3 notebook (parallel pipelines + memory persistence/recall)

---

## Troubleshooting

### sentence-transformers import errors
If you see errors mentioning `huggingface-hub` version requirements, upgrade:
- `pip install -U huggingface-hub transformers sentence-transformers`

### TensorFlow DLL load errors on Windows
If you see “Failed to load the native TensorFlow runtime”, TensorFlow is installed but broken in the environment.
This project does not require TensorFlow for embeddings; remove it:
- `pip uninstall -y tensorflow tensorflow-intel`

Then restart the kernel and rerun the notebook from the beginning.
