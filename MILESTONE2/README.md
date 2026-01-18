# Milestone 2 — Multi-Agent Reasoning, Coordination & Pipelines

## Overview

Milestone 2 focuses on building intelligent multi-agent reasoning on top of the Retrieval-Augmented Generation (RAG) system developed in Milestone 1. In this milestone, individual specialized agents (Legal, Compliance, Finance, Operations) are coordinated through rule-based routing, graph-based execution, shared memory, and collaborative validation. Finally, end-to-end pipelines are constructed for each domain and merged through a coordinator to produce a unified contract risk analysis.

The system continues to use:

* Pinecone vector database for semantic retrieval
* SentenceTransformer embeddings (all-MiniLM-L6-v2)
* HuggingFace LLM (google/gemma-2-2b-it) for agent reasoning
* Custom JSON validation for structured agent outputs

---

## 1. Coordinator Logic (Rule-Based Routing)

A rule-based coordinator is implemented to route user queries to the most relevant agent. Keyword-based routing rules map query intent to agents:

* Legal → termination, governing law, jurisdiction
* Compliance → gdpr, audit, regulatory, data protection
* Finance → payment, fee, penalty, invoice, indemnity
* Operations → deliverable, timeline, sla, milestone

A routing function selects relevant agents based on query keywords. The coordinator then loads previously saved agent outputs and returns only the selected agent results. This avoids running all agents unnecessarily and demonstrates controlled agent selection.

---

## 2. LangGraph Basics

LangGraph is introduced to model agents as graph nodes and define execution flows using edges.

A shared state object carries:

* user query
* individual agent outputs
* execution trace

Nodes representing Compliance and Legal agents are created. The execution order is modified to run:

Compliance → Legal → END

Print logs inside each node verify node execution order and shared state propagation.

---

## 3. Multi-Agent Graph Execution

All four agents (Legal, Compliance, Finance, Operations) are added as LangGraph nodes. A sequential execution graph is built:

Legal → Compliance → Finance → Operations → END

Alternative flows are tested:

* Changing execution order
* Removing one agent and observing missing state entries

This demonstrates how agent execution order affects shared state accumulation.

---

## 4. Conditional Routing in LangGraph

Conditional edges are added to LangGraph to dynamically select only one relevant agent based on the query content.

A routing function inspects the query and maps detected keywords to an agent node. Only the selected agent node executes, and then the graph terminates. Multiple test queries confirm correct agent selection for legal, finance, and compliance intents.

This demonstrates dynamic single-agent execution instead of running all agents.

---

## 5. Conversation Memory & State Persistence

A shared memory field is added to graph state to persist agent findings across nodes. Each agent:

* Reads domain-specific combined retrieved text
* Runs its LLM analysis
* Writes extracted clauses into shared memory

After graph execution, accumulated memory logs show the order of agent contributions, enabling multi-step reasoning and state persistence.

---

## 6. Agent-to-Agent Communication & Validation

Agents are extended to read shared memory and perform cross-agent validation.

* Compliance agent writes compliance findings to memory
* Finance agent reads compliance findings and adds validation notes regarding penalty conflicts
* Legal agent reads both compliance and finance findings and adds final enforceability checks

Validation notes are stored in shared state to demonstrate collaborative multi-agent verification.

An additional task extends this pattern where Operations agent reads Legal findings and validates SLA enforceability.

---

## 7. Domain-Specific Pipelines

End-to-end pipelines are constructed for each domain:

### Compliance Pipeline

* Defines compliance query template
* Retrieves compliance-related contract chunks using RAG
* Combines retrieved text
* Uses saved compliance agent output
* Generates compliance risk summary
* Saves final compliance pipeline output

### Finance Pipeline

* Defines finance query template
* Retrieves finance-related contract chunks
* Combines retrieved text
* Uses saved finance agent output
* Generates finance risk summary
* Saves final finance pipeline output

### Legal Pipeline

* Defines legal query template
* Retrieves legal-related contract chunks
* Combines retrieved text
* Uses saved legal agent output
* Generates legal risk summary
* Saves final legal pipeline output

### Operations Pipeline

* Defines operations query template
* Retrieves operations-related contract chunks
* Combines retrieved text
* Uses saved operations agent output
* Generates operations risk summary
* Saves final operations pipeline output

Each pipeline demonstrates chaining:
Retrieval → Context Building → Agent Reasoning → Validation → Risk Summary

---

## 8. Final Coordinator Merge

The final coordinator merges all pipeline outputs into a unified JSON structure:

* legal_analysis
* compliance_analysis
* finance_analysis
* operations_analysis

Additional logic computes:

* Overall confidence score (average of all agent confidences)
* Highest-risk clause across all agents

The merged result is saved as a final contract analysis report.

---

## Key Outcomes

* Intelligent routing selects relevant agents per query
* Graph-based execution controls agent workflow
* Shared memory enables multi-agent collaboration
* Domain pipelines produce validated structured outputs
* Coordinator merges all analyses into a final unified result

---
