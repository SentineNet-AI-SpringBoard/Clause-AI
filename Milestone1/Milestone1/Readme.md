**AI Tool to Read and Analyze Legal Contracts Automatically**

**Overview:**

This project presents an AI-based system that automatically reads, interprets, and analyzes legal contracts.
It uses a multi-agent architecture where specialized AI agents focus on different contract domains such as Legal, Compliance, Finance, and Operations.
Agent coordination is handled through LangGraph, enabling structured reasoning, collaboration, and scalable workflows.

**Key Features:**

- Upload and process contract files (PDF/TXT)

- Clause-level text segmentation with overlap

- Vector embedding generation

- Semantic clause retrieval using Pinecone

- Domain-specific AI agents

- Rule-based agent routing

- Multi-agent orchestration via LangGraph

- Shared memory between agents

- Cross-domain clause validation

**Technology Stack:**

**Programming Language**

- Python 3.10+

**Frameworks & Libraries**

- LangChain & LangGraph – Agent orchestration

- Pinecone – Vector database

- NumPy, Pandas – Data processing

- Matplotlib – Visualization

- Jupyter Notebook – Development & experiments

**Models Used:**

- Sentence Transformer (all-MiniLM-L6-v2) – Embeddings

- Google Gemma 2B IT – Agent reasoning
