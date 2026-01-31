# Clause-AI — Contract Analysis with Multi-Agent RAG

> **Intelligent contract analysis using Retrieval-Augmented Generation (RAG), multi-agent architecture, and persistent agent memory in Pinecone.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector%20DB-green)](https://www.pinecone.io/)
[![Transformers](https://img.shields.io/badge/HuggingFace-Transformers-orange)](https://huggingface.co/transformers/)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Milestone Deliverables](#milestone-deliverables)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**Clause-AI** is an advanced contract analysis system that combines:

- **RAG (Retrieval-Augmented Generation)**: Smart retrieval over contract documents using vector embeddings
- **Multi-Agent Architecture**: Specialized agents (Legal, Compliance, Finance, Operations) for domain-specific analysis
- **Persistent Agent Memory**: Stores agent outputs as vectors in Pinecone for instant recall without re-execution
- **Parallel Processing**: Async execution for 3-4x faster multi-agent runs

### Key Features

✅ **Vector-based contract search** using Pinecone  
✅ **4 specialized agents** (Legal, Compliance, Finance, Operations)  
✅ **Cross-agent verification** and risk escalation  
✅ **Persistent memory** — recall past agent outputs instantly  
✅ **Sequential vs. parallel** execution with timing comparisons  
✅ **Standard JSON outputs** with confidence scoring and evidence tracking

---

## 🏗️ Architecture

### System Components

```
┌─────────────────┐
│  Contract Docs  │
└────────┬────────┘
         │ Chunking + Embedding
         ▼
┌─────────────────┐      ┌──────────────────────┐
│  Pinecone       │ ──▶│  Contract Chunks     │
│  Vector DB      │      │  (namespace: default)│
└────────┬────────┘      └──────────────────────┘
         │
         │ Query + Retrieve
         ▼
┌─────────────────┐
│  Multi-Agent    │  ─┐
│  Coordinator    │   │ Legal Agent
│                 │   │ Compliance Agent
│                 │   │ Finance Agent
│                 │   └ Operations Agent
└────────┬────────┘
         │ Store Outputs
         ▼
┌─────────────────┐      ┌──────────────────────┐
│  Pinecone       │ ──▶│  Agent Memory        │
│  (memory ns)    │      │  (contract_id + agent)│
└─────────────────┘      └──────────────────────┘
```

### How It Works

1. **Ingestion** (Milestone 2)
   - Contract text → chunks → embeddings → Pinecone index
   
2. **Retrieval** (Milestone 2 + 3)
   - User query → embed → Pinecone search → top-k relevant chunks
   
3. **Multi-Agent Processing** (Milestone 3)
   - Each agent retrieves domain-specific context
   - Agents run in parallel (async) for speed
   - Cross-verification: Compliance reads Finance output to escalate risk
   
4. **Memory Persistence** (Milestone 3)
   - Agent outputs → embeddings → stored as vectors in `agent_memory` namespace
   - Later queries can recall stored outputs without re-running agents

---

## 📁 Project Structure

```
legal-contracts-eda/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variable template
├── .gitignore                   # Git ignore rules
│
├── milestone1/                  # Milestone 1: Project Setup & EDA
│   ├── Milestone1_ProjectPlanning_Setup_EDA.ipynb
│   ├── outputs/                 # EDA visualizations and summaries
│   └── README.md
│
├── milestone2/                  # Milestone 2: Pinecone + RAG
│   ├── Milestone2_Pinecone_VectorDB.ipynb
│   ├── outputs/                 # Agent outputs, RAG results
│   │   └── rag_results/         # Per-query retrieval results
│   └── README.md
│
├── milestone3/                  # Milestone 3: Parallel Agents + Memory
│   ├── Milestone3_ParallelAgents_PersistentMemory.ipynb
│   ├── outputs/                 # Final contract JSONs, coordinator cache
│   │   ├── final_contract_*.json
│   │   └── coordinator_cache/
│   └── README.md
│
├── milestone4/                  # Milestone 4: Streamlit UI + backend integration
│   ├── README.md
│   └── UI/
│
├── data/                        # Raw contract datasets (gitignored)
├── dataset/                     # Processed chunks & embeddings (gitignored)
├── artifacts/                   # Intermediate outputs (gitignored)
├── models_cache/                # HuggingFace model cache (gitignored)
└── venv/                        # Python virtual environment (gitignored)
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Pinecone account** (free tier available at [pinecone.io](https://www.pinecone.io/))
- **Hugging Face account** (optional, for gated models)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SentineNet-AI-SpringBoard/Clause-AI.git
   cd Clause-AI
   ```

2. **Create a Python virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env`:
   ```env
   # Required
   PINECONE_API_KEY=your_pinecone_api_key_here
   PINECONE_INDEX=cuad-index
   
   # Optional
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   CONTRACT_ID=demo_contract
   
   # Optional: Hugging Face token (for gated models)
   HF_TOKEN=your_hf_token_here
   ```

### Run the app (FastAPI backend + Streamlit UI)

1. **Start the backend**
   ```powershell
   cd milestone3\backend
   # Optional (recommended for Streamlit): allow the UI origin for CORS
   $env:FRONTEND_ORIGINS = "http://localhost:8501,http://127.0.0.1:8501"

   # Optional: seed demo users on startup (see Login section below)
   # $env:CLAUSEAI_DEMO_PASSWORD = "your-demo-password"

   uvicorn app:app --reload --port 8000
   ```

2. **Start the Streamlit UI**
   ```powershell
   cd milestone4\UI\UI
   pip install -r requirements.txt

   # Optional: point UI to a different backend base URL
   $env:BACKEND_URL = "http://127.0.0.1:8000"

   streamlit run app.py
   ```

Notes:
- Auth and analysis history are stored in a local SQLite DB on the backend.
- The UI currently supports **PDF uploads** (to enable preview + highlight features).

### Login (Milestone 4)

- You can **register** a new user in the UI.
- Optional: set `CLAUSEAI_DEMO_PASSWORD` before starting the backend to seed demo users.
  - Emails: `legal.demo@example.com`, `compliance.demo@example.com`, `finance.demo@example.com`, `operations.demo@example.com`, `admin.demo@example.com`
  - Password: whatever you set in `CLAUSEAI_DEMO_PASSWORD`

5. **Run notebooks in order**
   - Start with `milestone1/Milestone1_ProjectPlanning_Setup_EDA.ipynb`
   - Then `milestone2/Milestone2_Pinecone_VectorDB.ipynb`
   - Finally `milestone3/Milestone3_ParallelAgents_PersistentMemory.ipynb`

---

## 📊 Milestone Deliverables

### Milestone 1: Project Planning, Setup & EDA

**Notebook**: [`milestone1/Milestone1_ProjectPlanning_Setup_EDA.ipynb`](milestone1/Milestone1_ProjectPlanning_Setup_EDA.ipynb)

**Objectives**:
- Project initialization and environment setup
- Exploratory Data Analysis (EDA) on CUAD contract dataset
- Data profiling and quality assessment
- Initial contract structure understanding

**Outputs**:
- Dataset statistics and distributions
- Visualization of contract types and patterns
- Data quality reports
- Baseline metrics for downstream tasks

---

### Milestone 2: Pinecone Vector Database + RAG Implementation

**Notebook**: [`milestone2/Milestone2_Pinecone_VectorDB.ipynb`](milestone2/Milestone2_Pinecone_VectorDB.ipynb)

**Objectives**:
- Contract text chunking and preprocessing
- Vector embedding generation using sentence-transformers
- Pinecone index creation and vector upsertion
- RAG-based retrieval pipeline implementation
- Multi-agent framework (Legal, Compliance, Finance, Operations)

**Key Features**:
- **Smart chunking**: Preserves context while maintaining optimal chunk sizes
- **Semantic search**: Uses `all-MiniLM-L6-v2` for embeddings
- **Agent specialization**: Each agent has domain-specific retrieval queries
- **LangGraph integration**: State management and agent orchestration

**Outputs** (`milestone2/outputs/`):
- `rag_results/`: Per-query retrieval results with scores
- `*_agent_output.json`: Individual agent analysis outputs
- `agent_framework_summary.json`: System metadata and configuration

---

### Milestone 3: Parallel Agents + Persistent Memory

**Notebook**: [`milestone3/Milestone3_ParallelAgents_PersistentMemory.ipynb`](milestone3/Milestone3_ParallelAgents_PersistentMemory.ipynb)

**Objectives**:
- Implement parallel agent execution (asyncio)
- Timing comparison: Sequential vs. Parallel
- Persistent agent memory in Pinecone
- Cross-agent verification and risk escalation
- Final contract-level JSON output generation

**Key Innovations**:

1. **Parallel Execution**
   - Async/await pattern for agent coordination
   - 3-4x speedup compared to sequential runs
   - Thread pool for CPU-bound embedding operations

2. **Persistent Agent Memory**
   - Agent outputs stored as vectors in `agent_memory` namespace
   - Metadata: `contract_id`, `agent_type`, `timestamp`, `confidence`, `risk_level`
   - Instant recall without re-running agents

3. **Cross-Agent Verification**
   - Compliance agent reads Finance output
   - Risk escalation logic (e.g., MEDIUM → HIGH when financial penalties exceed threshold)
   - Evidence consolidation across agents

4. **Standard Output Format**
   ```json
   {
     "contract_id": "demo_contract",
     "timestamp": "2026-01-09T...",
     "agents": {
       "legal": { "summary": "...", "risk_level": "MEDIUM", "confidence": 0.82 },
       "compliance": { "summary": "...", "risk_level": "HIGH", "confidence": 0.75 },
       "finance": { "summary": "...", "risk_level": "MEDIUM", "confidence": 0.78 },
       "operations": { "summary": "...", "risk_level": "LOW", "confidence": 0.85 }
     },
     "overall_risk": "HIGH",
     "confidence_overall_avg": 0.80,
     "evidence_count": 47,
     "report_summary": "..."
   }
   ```

**Outputs** (`milestone3/outputs/`):
- `final_contract_*.json`: Standardized contract analysis reports
- `coordinator_cache/`: Intermediate coordinator state for debugging

---

## ⚙️ Configuration

### Environment Variables

The system uses a `.env` file for configuration. Never commit `.env` to Git!

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `PINECONE_API_KEY` | ✅ | Pinecone API key | `pcsk_...` |
| `PINECONE_INDEX` | ✅ | Pinecone index name | `cuad-index` |
| `PINECONE_ENV` | ❌ | Legacy Pinecone environment | (usually not needed) |
| `EMBEDDING_MODEL` | ❌ | Sentence transformer model | `all-MiniLM-L6-v2` |
| `CONTRACT_ID` | ❌ | Default contract identifier | `demo_contract` |
| `HF_TOKEN` | ❌ | Hugging Face API token | `hf_...` |
| `HUGGINGFACEHUB_API_TOKEN` | ❌ | Alternative HF token name | `hf_...` |

#### Backend + UI variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `BACKEND_URL` | ❌ | Streamlit UI → backend base URL | `http://127.0.0.1:8000` |
| `FRONTEND_ORIGINS` | ❌ | Backend CORS allowlist (comma-separated origins) | `http://127.0.0.1:8501` |
| `CLAUSEAI_BACKEND_DB_PATH` | ❌ | SQLite DB path for auth/history | `milestone3/outputs/clauseai_backend.sqlite3` |
| `CLAUSEAI_SESSION_TTL_HOURS` | ❌ | Session lifetime (hours) | `72` |
| `CLAUSEAI_DEMO_PASSWORD` | ❌ | Enables demo-user seeding on backend startup | `your-demo-password` |

### Pinecone Setup

1. Sign up at [pinecone.io](https://www.pinecone.io/)
2. Create a new index:
   - **Name**: `cuad-index`
   - **Dimensions**: `384` (for `all-MiniLM-L6-v2`)
   - **Metric**: `cosine`
   - **Cloud/Region**: Choose closest to you
3. Copy your API key to `.env`

### Model Configuration

The system uses these models by default:

- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384-dim)
- **LLM** (Milestone 2): `google/gemma-2b-it` (for agent text generation)

Models are cached in `models_cache/` (gitignored).

---

## 🔧 Troubleshooting

### Common Issues

#### 1. `ImportError: No module named 'sentence_transformers'`

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

#### 2. Hugging Face token errors

**Problem**: `401 Unauthorized` when downloading gated models

**Solution**: Set your HF token in `.env`
```env
HF_TOKEN=hf_your_token_here
```

Get token at: https://huggingface.co/settings/tokens

#### 3. TensorFlow DLL errors on Windows

**Problem**: `Failed to load the native TensorFlow runtime`

**Solution**: This project doesn't need TensorFlow. Uninstall it:
```bash
pip uninstall -y tensorflow tensorflow-intel
```

Then restart the notebook kernel.

#### 4. Pinecone connection errors

**Problem**: `PineconeException: Invalid API key`

**Solutions**:
- Verify `.env` is in the repo root directory
- Check `PINECONE_API_KEY` has no extra spaces/quotes
- Ensure the notebook loaded `.env` (check cell 2 output in Milestone 2/3)

#### 5. Version conflicts (huggingface-hub, transformers)

**Problem**: `ImportError: cannot import name ... from 'huggingface_hub'`

**Solution**: Upgrade packages
```bash
pip install -U huggingface-hub transformers sentence-transformers
```

#### 6. Memory errors during parallel execution

**Problem**: Notebook crashes or freezes during async agent runs

**Solutions**:
- Reduce batch size in parallel execution
- Close other applications to free memory
- Run agents sequentially instead of parallel (slower but more stable)

---

## 📈 Performance Metrics

### Execution Time Comparison (Milestone 3)

| Mode | Runtime | Speedup |
|------|---------|---------|
| Sequential | ~45-60s | 1x (baseline) |
| Parallel (async) | ~12-18s | **3-4x faster** |

*Tested on: Windows 11, 12-core CPU, 16GB RAM*

### Agent Recall Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Agent execution (cold) | ~40-50s | All 4 agents from scratch |
| Memory recall (warm) | ~2-3s | Fetch stored outputs from Pinecone |

**Speedup**: ~20x faster for repeated queries on same contract

---

## 🛠️ Technology Stack

- **Python 3.8+**: Core language
- **Pinecone**: Vector database for embeddings and agent memory
- **sentence-transformers**: Text embedding generation
- **HuggingFace Transformers**: LLM integration (Gemma 2B)
- **LangChain/LangGraph**: Agent orchestration and state management
- **asyncio**: Parallel agent execution
- **python-dotenv**: Environment variable management
- **pandas**: Data analysis and EDA
- **tqdm**: Progress bars

---

## 📝 Key Concepts

### RAG (Retrieval-Augmented Generation)

Traditional LLMs hallucinate or lack domain-specific knowledge. RAG solves this by:
1. Retrieving relevant context from a vector database
2. Augmenting the LLM prompt with retrieved facts
3. Generating responses grounded in real data

### Multi-Agent Architecture

Instead of one general-purpose agent, we use specialized agents:
- **Legal**: Termination, breach, confidentiality, indemnification
- **Compliance**: Privacy, regulatory, audit, data retention
- **Finance**: Fees, invoices, penalties, liability caps
- **Operations**: Deliverables, SLAs, timelines, performance standards

Each agent:
- Has domain-specific retrieval queries
- Generates structured JSON outputs
- Assigns risk levels and confidence scores

### Persistent Agent Memory

After running agents, we don't discard outputs. Instead:
1. Embed agent output text as a vector
2. Store in Pinecone with metadata (`contract_id`, `agent_type`, etc.)
3. Later queries can recall outputs without re-execution

**Benefits**:
- 20x faster retrieval vs. re-running agents
- Historical tracking of agent analyses
- Easy comparison across contract versions

---

## 🤝 Contributing

This is a milestone-based project for educational/research purposes. Contributions are welcome!

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make changes and test thoroughly
4. Commit with clear messages (`git commit -m "Add: feature description"`)
5. Push to your fork (`git push origin feature/your-feature`)
6. Open a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings to functions/classes
- Keep notebook cells focused and well-documented

---

## 📄 License

This project is developed as part of the SentineNet AI SpringBoard program.

---

## 🙏 Acknowledgments

- **CUAD Dataset**: Contract Understanding Atticus Dataset
- **Pinecone**: For scalable vector database infrastructure
- **Hugging Face**: For open-source transformers and embedding models
- **SentineNet AI SpringBoard**: For project guidance and support

---

## 📧 Contact

For questions or issues:
- **Repository**: [Clause-AI GitHub](https://github.com/SentineNet-AI-SpringBoard/Clause-AI)
- **Issues**: [Report a bug or request a feature](https://github.com/SentineNet-AI-SpringBoard/Clause-AI/issues)

---

**Built with ❤️ for intelligent contract analysis**
