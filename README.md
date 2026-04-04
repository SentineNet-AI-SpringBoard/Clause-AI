## CLAUSE AI 
# ClauseAI — AI-Powered Legal Contract Analysis Tool

ClauseAI is an AI-powered system that automates the reading and analysis of legal contracts using a multi-agent framework. Each agent specializes in a distinct domain — compliance, finance, risk, and operations — to deliver precise, actionable insights and professional reports.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Workflow](#workflow)
- [Installation](#installation)
- [Project Milestones](#project-milestones)
- [Author](#author)

---

## Overview

Manual contract review is slow, tedious, and prone to human error. ClauseAI tackles this by deploying specialized AI agents that collaborate in parallel — scanning every clause, flagging risks, checking compliance, and extracting financial terms — then packaging it all into a clean, customizable report in seconds.

This project was built as part of an internship to explore practical applications of multi-agent AI systems in the legal tech domain.

---

## Features

- Multi-format contract upload — PDF, DOCX, TXT, and external legal APIs
- Coordinator agent that plans and manages all domain-specific agents
- Automatic clause identification, risk flagging, and compliance checking
- Financial term extraction — payment schedules, penalties, liability caps
- Parallel processing for fast analysis of large or multiple contracts
- Human feedback loop to refine and re-focus analysis
- Semantic search across contracts using Pinecone vector database
- Customizable report generation — tone, format, and section control
- Interactive UI built with Streamlit / Gradio

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.x | Core language |
| LangGraph | Multi-agent graph orchestration |
| LangChain | LLM chaining and prompt management |
| OpenAI API | Language understanding and generation |
| Pinecone | Vector database for semantic search |
| PyPDF2 / python-docx | Document parsing |
| Streamlit / Gradio | User interface |

---

## Workflow

```
1. INPUT      →  User uploads a contract document (PDF / DOCX / TXT)
2. PLANNING   →  Coordinator agent assigns tasks to domain specialist agents
3. ANALYSIS   →  Agents run in parallel — clauses identified, risks scored
4. REPORTING  →  All outputs synthesized into a professional downloadable report
```

---

## Installation

**Prerequisites:** Python 3.8+, OpenAI API key, Pinecone API key

```bash
# Clone the repository
git clone https://github.com/your-username/clauseai.git
cd clauseai

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Open .env and add your OpenAI and Pinecone API keys

# Initialize Pinecone index
python scripts/init_pinecone.py

# Run the app
streamlit run app.py
```

Open `http://localhost:8501` in your browser to get started.

---

## Project Milestones

**Weeks 1–2 — Foundation**
Set up the environment with LangGraph, LangChain, and Pinecone. Built the document upload module with PDF and DOCX parsing. Defined the agent role structure and ran initial tests on sample contracts.

**Weeks 3–4 — Planning & Coordination**
Developed the Planning Module for dynamic agent generation. Implemented API integration for contract upload, designed domain-specific prompt templates, and validated inter-agent coordination using LangGraph.

**Weeks 5–6 — Parallel Analysis Engine**
Implemented parallel processing with a map-reduce architecture. Built pipelines for compliance and financial risk analysis. Tested multi-turn agent interactions and integrated Pinecone for intermediate result storage.

**Weeks 7–8 — Reporting, UI & Finalization**
Built the Report Generation Module with customizable tone and structure. Designed and implemented the full UI. Added human feedback loop, optimized for concurrent contracts, and completed all documentation.

---

## Author

Intern — AI / Machine Learning


---

*Built with dedication using Python and other amazing open-source tools.*
