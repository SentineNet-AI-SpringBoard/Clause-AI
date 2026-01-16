#  CLAUSEAI

### AI Tool to Read and Analyze Legal Contracts Automatically

---

## 📌 Project Overview

ClauseAI is an AI-powered system designed to **automate legal contract analysis**, improving efficiency and precision while generating customized, actionable reports.
It leverages a **Retrieval-Augmented Generation (RAG)** pipeline combined with a **multi-agent architecture**, where each AI agent specializes in a distinct contract domain such as **Legal, Compliance, Finance, and Operations**.

This project implements an end-to-end pipeline to:

* Read contract documents
* Retrieve relevant clauses using semantic search
* Analyze risks using specialized AI agents
* Produce structured, traceable risk reports

The overall objective and workflow follow the design described in the project document:
“ClauseAI is an AI-powered system designed to automate the process of contract analysis, leveraging a multi-agent framework where each AI agent specializes in a distinct domain such as compliance, finance, and operations to deliver comprehensive insights.” 

---

## 🎯 Project Objectives

* Automate extraction of key contract clauses
* Perform semantic search using Pinecone vector database
* Implement RAG-based retrieval for relevant context
* Build domain-specific AI agents:

  * Legal Risk Agent
  * Compliance Risk Agent
  * Finance Risk Agent
  * Operations Risk Agent
* Assess contract risk levels (Low / Medium / High)
* Generate traceable and reproducible JSON reports

---

## 🏗️ Project Structure

```
CLAUSEAI/
│
├── dataset/
│   ├── chunks/              # Contract chunks (JSON)
│   └── embeddings/          # Embeddings (JSON)
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
│       └── operations_agent_output.json
│
├── Data/
│   └── Raw/
│       ├── full_contract_txt/
│       ├── CUAD_v1.json
│       └── master_clauses.csv
│
├── requirements.txt
└── README.md
```
### How It Works
1. [cite_start]**Classify**: Identifies the contract type[cite: 24].
2. [cite_start]**Retrieve**: Extracts relevant clauses via Pinecone[cite: 25, 44].
3. [cite_start]**Plan**: Coordinator agent assigns tasks to specialized domains[cite: 8].
4. [cite_start]**Execute**: Parallel processing executes multiple analyses concurrently[cite: 18].
5. [cite_start]**Report**: Synthesizes outputs into a professional summary[cite: 14].

---

## 📂 Project Structure
```text
Clause-AI/
├── milestone1/        # Project Planning, Setup & EDA
├── milestone2/        # Agent Coordination & Classification
├── milestone3/        # Parallel Processing & Risk Analysis
├── .env.example       # Template for environment variables
├── requirements.txt   # Python dependencies
└── README.md          # Main documentation

## 🧰 Technology Stack

**Programming Language:** Python 3.x

**Libraries & Frameworks:**

* SentenceTransformers (`all-MiniLM-L6-v2`)
* Pinecone Vector Database
* RAG Retrieval Pipeline
* Multi-Agent LLM Framework
* JSON-based artifacts

The project technology stack is aligned with the system design described in the project document. 

---

## 🚀 How to Run

1. Install dependencies:

```
pip install -r requirements.txt
```

2. Run Milestone 1 notebook:

```
Notebooks/Milestone1_Planning_&_Setup.ipynb
```

3. Run Milestone 2 notebook:

```
Notebooks/Milestone2.ipynb
```

4. Outputs generated at:

```
Notebooks/output/
```

---

ClauseAI delivers an **end-to-end AI-based contract analysis system** using RAG and multi-agent architecture, enabling automated legal, compliance, finance, and operational risk detection from complex contracts.
