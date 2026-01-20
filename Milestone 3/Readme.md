# ClauseAI – Multi-Agent Contract Analysis System

## Overview

ClauseAI is a smart contract analysis platform that leverages multiple specialized agents to extract, check, and evaluate contractual clauses across areas like Legal, Compliance, Finance, and Operations. Built on a modular architecture with LangGraph, it enables collaborative reasoning and scalable analysis workflows.

## Key Features

* Ingest and preprocess contracts (PDF/TXT)
* Chunk clauses with overlap for better context
* Generate embeddings and store in vector databases
* Semantic search using vector retrieval
* Domain-specific agents: Legal, Compliance, Finance, Operations
* Conditional routing and rule-based processing
* Orchestration of multiple agents with LangGraph
* Shared memory for agent communication
* Cross-domain validation and analysis

## Tech Stack

* **Programming Language:** Python 3.10+
* **Libraries & Frameworks:**

  * LangChain & LangGraph (agent orchestration)
  * Pinecone (vector storage and search)
  * NumPy, Pandas (data processing)
  * Matplotlib (visualizations)
  * Jupyter Notebook (experimentation)

## Models Used

* Sentence-Transformer / Hugging Face for embeddings
* Gemma model for agent reasoning

## Challenges

* Used API key for the all-minilm-l6-v2 embedding model
* Tested larger models like Qwen2.5 and Mistral-7B, but limited 16GB RAM prevented loading; gemma-2b-it was adopted instead

