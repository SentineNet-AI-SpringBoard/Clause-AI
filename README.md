

***

# Clause-AI: Multi-Agent Contract Analysis with RAG & Persistent Memory

**Intelligent contract review using Retrieval-Augmented Generation (RAG), specialized agents, and Pinecone vector storage.**

**Tech Stack:** Python -  Pinecone -  Transformers -  LangGraph -  Async Agents

## 🚀 Quick Start

```bash
git clone https://github.com/SentineNet-AI-SpringBoard/Clause-AI.git
cd Clause-AI
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add your Pinecone API key
```

Run notebooks sequentially: `milestone1` → `milestone2` → `milestone3`

## 🎯 Core Features

- **Vector Search**: Pinecone-powered semantic retrieval over contract chunks
- **4 Specialized Agents**: Legal, Compliance, Finance, Operations
- **3-4x Speedup**: Parallel async execution vs sequential
- **Persistent Memory**: Recall agent outputs instantly (20x faster)
- **Cross-Agent Verification**: Compliance validates Finance risks
- **JSON Outputs**: Confidence scores, risk levels, evidence tracking

## 🏗️ Architecture Overview

```
Contract Docs → Chunking → Embeddings → Pinecone (default namespace)
                       ↓
User Query → Retrieve Context → Multi-Agent Coordinator
                       ↓
4 Agents (Parallel) → Store Outputs → Pinecone (agent_memory namespace)
```

## 📁 Project Structure

```
legal-contracts-eda/
├── milestone1/     # EDA & Setup
├── milestone2/     # Pinecone + RAG
├── milestone3/     # Parallel Agents + Memory
├── milestone4/     # Streamlit UI
├── data/           # Contracts (gitignored)
├── requirements.txt
└── .env.example
```

## 📊 Milestones & Deliverables

### Milestone 1: EDA & Setup
**Notebook:** `milestone1/Milestone1_ProjectPlanning_Setup_EDA.ipynb`
- CUAD dataset profiling
- Contract structure analysis
- Baseline metrics

**Outputs:** Dataset stats, visualizations, quality reports

### Milestone 2: Pinecone RAG Pipeline
**Notebook:** `milestone2/Milestone2_Pinecone_VectorDB.ipynb`
- Text chunking + `all-MiniLM-L6-v2` embeddings
- Pinecone index setup (384-dim, cosine)
- Agent-specific retrieval queries

**Outputs:** `rag_results/`, agent JSONs, framework summary

### Milestone 3: Parallel Agents + Memory
**Notebook:** `milestone3/Milestone3_ParallelAgents_PersistentMemory.ipynb`
- Async execution (12-18s vs 45-60s sequential)
- Agent memory in Pinecone (`agent_memory` namespace)
- Risk escalation logic
- Final JSON reports

**Sample Output:**
```json
{
  "contract_id": "demo_contract",
  "overall_risk": "HIGH",
  "confidence_overall_avg": 0.80,
  "agents": {
    "legal": {"risk_level": "MEDIUM", "confidence": 0.82},
    "compliance": {"risk_level": "HIGH", "confidence": 0.75},
    "finance": {"risk_level": "MEDIUM", "confidence": 0.78},
    "operations": {"risk_level": "LOW", "confidence": 0.85}
  }
}
```

## ⚙️ Configuration

**`.env` (required):**
```
PINECONE_API_KEY=your_key_here
PINECONE_INDEX=cuad-index
EMBEDDING_MODEL=all-MiniLM-L6-v2
CONTRACT_ID=demo_contract
HF_TOKEN=your_hf_token  # Optional
```

**Pinecone Setup:**
1. Create index: `cuad-index` (384 dimensions, cosine metric)
2. Copy API key to `.env`

## ⏱️ Performance

| Mode | Time | Speedup |
|------|------|---------|
| Sequential | 45-60s | 1x |
| Parallel | 12-18s | **3-4x** |
| Memory Recall | 2-3s | **20x** |

*Tested: Windows 11, 12-core CPU, 16GB RAM*

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `sentence_transformers` missing | `pip install -r requirements.txt` |
| HF 401 errors | Add `HF_TOKEN` to `.env` |
| Pinecone auth | Check `.env` key format |
| Memory crashes | Reduce batch size or run sequential |

## 🛠️ Tech Stack

- **Vector DB**: Pinecone (embeddings + agent memory)
- **Embeddings**: `all-MiniLM-L6-v2` (384-dim)
- **LLM**: `google/gemma-2b-it`
- **Agents**: LangGraph orchestration
- **Parallel**: asyncio + thread pools


***

## 🙌 Acknowledgments

- **CUAD Dataset**: Contract Understanding Atticus Dataset for comprehensive legal contract benchmarking
- **Pinecone**: Scalable vector database powering RAG and agent memory
- **Hugging Face**: Open-source Transformers, embeddings (`all-MiniLM-L6-v2`), and Gemma-2B
- **SentineNet AI SpringBoard**: Project guidance, mentorship, and infrastructure support

***


