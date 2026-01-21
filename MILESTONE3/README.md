##  Milestone 3 – Parallel Agents & Persistent Memory

### Objective

This milestone focuses on executing multiple contract-analysis agents in **parallel**, persisting their outputs into a **vector database**, enabling **memory recall**, performing **cross-agent refinement**, and generating a **final structured contract report** through a backend API.

---

## Key Features Implemented

### 1. Parallel Agent Execution with LangGraph

- Built a parallel LangGraph where Legal, Compliance, Finance, and Operations agents run concurrently.
- Implemented fan-out execution from a single START node.
- Added timing logs to measure per-agent and total runtime.
- Compared sequential vs parallel performance.

**Outcome:**  
All agents execute simultaneously, reducing total contract analysis time.

---

### 2. Persisting Agent Outputs into Memory (Vector DB)

- Converted agent outputs into textual records.
- Embedded records using SentenceTransformer embeddings.
- Stored vector records into Pinecone with metadata:
  - `agent_name`
  - `contract_id`
  - `timestamp`

**Outcome:**  
Agent knowledge is stored for later retrieval and reuse.

---

### 3. Querying Stored Agent Memory (Recall & Reuse)

- Implemented retrieval queries to recall past agent outputs.
- Enabled memory-based reasoning for future contract analysis.
- Verified correct storage and retrieval from vector DB.

**Outcome:**  
System supports persistent long-term agent memory.

---

### 4. Cross-Agent Refinement

- Enabled agents to read outputs of other agents.
- Legal agent performs final consistency validation.
- Generated validation notes for conflict detection.

**Outcome:**  
Improved accuracy through collaborative multi-agent refinement.

---

### 5. Final Contract-Level JSON Output

- Merged outputs from all agents.
- Computed overall risk score.
- Identified highest-risk clauses.
- Produced unified structured JSON result.

**Outcome:**  
Single standardized contract-analysis result for downstream use.

---

### 6. Human-Readable Report Generation

- Designed a report template.
- Converted JSON results into formatted text report.
- Adjusted tone for professional legal readability.

**Outcome:**  
Generated a client-ready contract analysis report.

---

### 7. FastAPI Backend for Contract Analysis

- Implemented backend API endpoint.
- Accepts uploaded contract files.
- Runs full RAG → Agents → Report pipeline.
- Returns final structured JSON and report.

**Outcome:**  
End-to-end contract analysis service accessible via REST API.

---

## Technologies Used

- **LangGraph** – Parallel multi-agent orchestration  
- **Pinecone** – Vector database for persistent memory  
- **SentenceTransformers** – Embeddings (`all-MiniLM-L6-v2`)  
- **HuggingFace LLM** – `google/gemma-2-2b-it`  
- **FastAPI** – Backend service  
- **Python 3.11**

---

## How to Run

1. Ensure Pinecone index is created and embeddings are loaded.
2. Run Milestone-3 notebook cells sequentially.
3. Execute parallel agent graph.
4. Verify vector DB storage.
5. Run FastAPI backend for API testing.

---

## Milestone 3 Achievements

✔ Parallel multi-agent execution  
✔ Persistent vector memory  
✔ Memory recall and reuse  
✔ Cross-agent validation  
✔ Unified contract JSON  
✔ Human-readable reports  
✔ Backend API integration  

