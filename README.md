# Clause-AI

# 📑 CLAUSEAI — Multi-Agent Contract Risk Analysis using RAG

## 📌 Project Overview

CLAUSEAI is an AI-powered contract analysis system that uses **Retrieval-Augmented Generation (RAG)** and **multi-agent LLM architecture** to automatically extract, analyze, and assess risks from legal contracts.

The system processes raw contract documents, creates semantic embeddings, stores them in a Pinecone vector database, retrieves relevant contract clauses using RAG, and passes them to specialized AI agents to detect risks in different domains.

---

## 🎯 Project Objectives

* Extract relevant contract clauses using semantic search (RAG)
* Build domain-specific AI agents for:

  * Legal Risk Analysis
  * Compliance Risk Analysis
  * Finance Risk Analysis
  * Operations Risk Analysis
* Assess risk levels (Low / Medium / High)
* Store traceable outputs for reproducibility

---

## 🏗️ Project Structure

```
CLAUSEAI/
│
├── Data/
│   ├── Raw/
│   │   ├── full_contract_txt/
│   │   ├── CUAD_v1.json
│   │   └── master_clauses.csv
│   └── dataset/
│       ├── chunks/
│       └── embeddings/
│
├── Notebooks/
│   ├── Milestone1_Planning_&_Setup.ipynb
│   ├── Milestone2.ipynb
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
│       ├── operations_agent_output.json
│
├── Apps/
├── Artifacts/
├── requirements.txt
└── README.md
```

---

## ⚙️ Pipeline Workflow

### **1. Data Preparation**

* Raw contract texts loaded from CUAD dataset
* Contracts cleaned and split into semantic chunks
* Metadata such as contract_id, chunk_index, word_count stored

### **2. Embedding Generation**

* SentenceTransformer model: `all-MiniLM-L6-v2`
* Embeddings generated for each chunk
* Stored as JSON files in `dataset/embeddings/`

### **3. Pinecone Vector Database**

* Pinecone index created (`cuad-index`)
* Embeddings + metadata upserted
* Enables semantic similarity search

### **4. RAG Search Wrapper**

* User queries converted to embeddings
* Pinecone retrieves top-k relevant chunks
* Results saved as traceable JSON files in:

  ```
  Notebooks/output/rag_search_results/
  ```

---

## 🤖 Multi-Agent Architecture

Each agent receives RAG-retrieved context and performs specialized analysis.

### 🧑‍⚖️ Legal Agent

* Identifies legal clauses (Termination, Jurisdiction, Governing Law)
* Extracts clause text
* Assesses legal risk

Output:

```
Notebooks/output/legal_agent_output.json
```

---

### 🛡️ Compliance Agent

* Detects regulatory & policy risks
* Focus on GDPR, SOC2, ISO27001, HIPAA
* Extracts compliance obligations
* Assesses compliance risk

Output:

```
Notebooks/output/compliance_agent_output.json
```

---

### 💰 Finance Agent

* Identifies payment terms, penalties, late fees
* Detects financial liabilities and indemnifications
* Assesses financial risk

Output:

```
Notebooks/output/finance_agent_output.json
```

---

### ⚙️ Operations Agent

* Extracts deliverables, timelines, milestones
* Identifies SLAs and performance standards
* Assesses execution risk

Output:

```
Notebooks/output/operations_agent_output.json
```

---

## 📊 Risk Levels

| Risk Level | Description                                                         |
| ---------- | ------------------------------------------------------------------- |
| LOW        | Standard terms, clear obligations, reasonable conditions            |
| MEDIUM     | Some ambiguity, moderate penalties, partial compliance              |
| HIGH       | Harsh penalties, unclear obligations, missing regulatory safeguards |

---

## 💾 Traceability

All RAG search queries are saved as JSON files to ensure:

* Full traceability of retrieved clauses
* Reproducibility of agent decisions
* Debugging and auditability

---

## 🧰 Tech Stack

* Python
* SentenceTransformers (`all-MiniLM-L6-v2`)
* Pinecone Vector Database
* OpenAI / LLM-based BaseAgent Framework
* JSON-based traceable artifacts

---

## 🚀 How to Run

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Run Milestone 1 Notebook:

```
Notebooks/Milestone1_Planning_&_Setup.ipynb
```

3. Run Milestone 2 Notebook:

```
Notebooks/Milestone2.ipynb
```

4. Outputs will be saved in:

```
Notebooks/output/
```

---

## 📌 Key Highlights

* End-to-End RAG pipeline for contract analysis
* Multi-agent specialization for domain risks
* Traceable and reproducible outputs
* Scalable architecture for future extensions

---

## 👩‍🎓 Student Project

This project was developed as part of an AI-based Legal Contract Analysis system using RAG and multi-agent LLM architecture.

---

## ✅ Final Outputs

```
Notebooks/output/
├── legal_agent_output.json
├── compliance_agent_output.json
├── finance_agent_output.json
└── operations_agent_output.json
```

Each file contains:

* Extracted clauses
* Risk level
* Confidence score
* Supporting evidence

---



