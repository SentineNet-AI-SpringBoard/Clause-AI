
***

# ClauseAI: AI-Powered Contract Analysis

## Project Overview

ClauseAI automates contract review with specialized AI agents for **legal**, **compliance**, **finance**, and **operations** domains. It delivers precise, actionable insights through multi-agent collaboration, reducing manual review time while ensuring comprehensive coverage.

##  System Architecture & Workflow

```
Input → Coordinator → Domain Agents → Parallel Analysis → Unified Report
```

**Core Phases**:

1. **Input**: Upload contracts or connect legal APIs  
2. **Planning**: Coordinator routes to domain agents  
3. **Analysis**: Multi-turn agent discussions + parallel extraction  
4. **Reporting**: Synthesize into professional summaries  

##  Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.x |
| Orchestration | LangChain, LangGraph |
| Vector DB | Pinecone |
| Models | Gemma-2b-it (production), OpenAI (architecture) |
| Parsing | PyPDF2, python-docx |
| Frontend | Streamlit |

***

##  Milestone Progress

### Milestone 1: RAG Pipeline  Complete

**Focus**: Environment setup + retrieval foundation

**Data Pipeline**:

- **Source**: 510 contracts (`full_contract_txt/`)  
- **Processing**: LangChain chunking → `all-MiniLM-L6-v2` embeddings → Pinecone storage  
- **Output**: 20 RAG context files for agents  

**Challenges & Solutions**:
| Issue | Resolution |
|-------|------------|
| SentenceTransformer API key | Direct model loading |
| Large models (Qwen2.5, Mistral-7B) | Switched to Gemma-2b-it (fits 16GB RAM) |

### Milestone 2: Agent Orchestration  Complete

**Focus**: Multi-agent coordination + LangGraph implementation

**Pipeline Details**:

- **Input**: 4 JSON files (Legal/Compliance/Finance/Operations from Gemma-2b-it)  
- **Processing**: Keyword-based routing → LangGraph nodes → Shared memory  
- **Flow**: Legal (entry) → Compliance (writes risks) → Finance (reads/validates) → Legal (final validation)  

**Challenges & Solutions**:

| Issue | Resolution |
|-------|------------|
| Empty agent outputs | Fixed JSON pre-compute storage |

### Milestone 3: Parallel Processing  In Progress

**Current Work**:
-  Multi-domain parallel extraction  
-  Cross-refinement with Pinecone storage  
-  `app.py` API endpoints (Postman testing)  

**Next**: Live API deployment + Streamlit integration

***

**Key Achievements**:

- Zero-hallucination RAG pipeline  
- Memory-enabled agent collaboration  
- Scalable LangGraph orchestration  
- Production-ready Gemma-2b-it deployment  

**GitHub Ready** | **Streamlit Deployable** | **API Endpoint Complete (Milestone 3)**

***

