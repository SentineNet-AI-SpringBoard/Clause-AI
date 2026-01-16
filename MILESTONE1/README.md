# CLAUSEAI — Milestone 1

---

## 📌 Milestone 1 Overview

Milestone 1 focuses on building the **core Retrieval-Augmented Generation (RAG) pipeline** and **domain-specific AI agents** for automated contract risk analysis.

By the end of this milestone, the system is capable of:

* Chunking legal contracts
* Generating embeddings
* Storing vectors in Pinecone
* Retrieving relevant clauses via RAG
* Running specialized agents for risk assessment

---

## 🎯 Milestone 1 Objectives

✔ Prepare and preprocess contract data
✔ Generate semantic embeddings
✔ Build Pinecone vector database
✔ Implement RAG search wrapper
✔ Create multi-agent architecture:

* Legal Agent
* Compliance Agent
* Finance Agent
* Operations Agent

✔ Save all RAG and Agent outputs for traceability

---

## 🏗️ Project Structure (Milestone 1)

```
CLAUSEAI/
│
├── dataset/
│   ├── chunks/              # Contract chunks (JSON)
│   └── embeddings/          # Embeddings (JSON)
│
├── Notebooks/
│   ├── Milestone1_Planning_&_Setup.ipynb
│   └── output/
│       ├── rag_search_results/
│       │   ├── rag_legal_*.json
│       │   ├── rag_compliance_*.json
│       │   ├── rag_finance_*.json
│       │   └── rag_operations_*.json
│       │
│       ├── legal_agent_output.json
│       ├── compliance_agent_output.json
│       ├── finance_agent_output.json
│       └── operations_agent_output.json
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Milestone 1 Workflow

### **1. Contract Preprocessing**

* Raw contract text cleaned
* Documents split into semantic chunks
* Metadata (contract_id, chunk_index, length stats) added

---

### **2. Embedding Generation**

* Model used: `SentenceTransformer(all-MiniLM-L6-v2)`
* Embeddings generated for each chunk
* Saved under `dataset/embeddings/`

---

### **3. Pinecone Vector Database**

* Pinecone index created (`cuad-index`)
* Embeddings + metadata upserted
* Enables semantic similarity search

---

### **4. RAG Search Wrapper**

* Query converted to embedding
* Pinecone retrieves top-k relevant chunks
* Each RAG query result saved under:

```
Notebooks/output/rag_search_results/
```

This ensures full traceability of retrieval results.

---

## 🤖 Multi-Agent System (Milestone 1)

Each agent receives retrieved RAG context and performs domain-specific risk analysis.

---

### 🧑‍⚖️ Legal Agent

**Purpose:**
Extracts legal clauses such as termination, governing law, jurisdiction, indemnification.

**Output File:**

```
Notebooks/output/legal_agent_output.json
```

---

### 🛡️ Compliance Agent

**Purpose:**
Detects regulatory and policy risks focusing on:

* GDPR
* SOC2
* ISO 27001
* HIPAA

**Output File:**

```
Notebooks/output/compliance_agent_output.json
```

---

### 💰 Finance Agent

**Purpose:**
Analyzes financial obligations including:

* Payment terms
* Late fees and penalties
* Interest charges
* Financial liabilities

**Output File:**

```
Notebooks/output/finance_agent_output.json
```

---

### ⚙️ Operations Agent

**Purpose:**
Extracts operational obligations such as:

* Deliverables
* Timelines and milestones
* SLAs and uptime commitments
* Performance standards

**Output File:**

```
Notebooks/output/operations_agent_output.json
```

---

## 📊 Risk Classification

| Risk Level | Meaning                                    |
| ---------- | ------------------------------------------ |
| LOW        | Clear obligations, standard clauses        |
| MEDIUM     | Partial ambiguity, moderate risk           |
| HIGH       | Harsh terms, unclear or missing safeguards |

---

## 💾 Traceability

Every RAG query result is stored as JSON.
This ensures:

* Clause retrieval traceability
* Reproducible agent decisions
* Easy debugging and auditing

---

## 🧰 Technologies Used

* Python
* SentenceTransformers (`all-MiniLM-L6-v2`)
* Pinecone Vector Database
* RAG Retrieval Pipeline
* Multi-Agent LLM Framework
* JSON-based artifacts

---

## 🚀 How to Run Milestone 1

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Run Notebook:

```
Notebooks/Milestone1_Planning_&_Setup.ipynb
```

3. Outputs generated under:

```
Notebooks/output/
```

---

## ✅ Milestone 1 Completion Summary

✔ Contract chunking and preprocessing
✔ Embedding generation
✔ Pinecone vector database setup
✔ RAG retrieval system
✔ Legal Agent built
✔ Compliance Agent built
✔ Finance Agent built
✔ Operations Agent built

---

## 📌 Next Milestone

**Milestone 2** will extend the system with:

* Multi-agent orchestration
* Cross-agent reasoning
* Final unified contract risk report
* UI integration

---

## 🎉 Milestone 1 Successfully Completed

End-to-end RAG + Multi-Agent Contract Analysis pipeline implemented.
