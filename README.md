# AI Tool to Read and Analyze Legal Contracts Automatically

## Milestone 1 – RAG Pipeline Setup & Initial Testing
[View Milestone 1](Milestone1/Readme.md)

## Milestone 2 – Multi-Agent Orchestration & Planning Module
[View Milestone 2](Milestone%202/Readme.md)


**Milestone 1 – RAG Pipeline Setup & Initial Testing**
**Objective**

The first milestone focused on setting up the environment and building a Retrieval-Augmented Generation (RAG) pipeline.
The aim was to enable document ingestion, vector storage, and initial testing of domain-specific AI agents.

**Completed Tasks**

* Configured sentence-transformer embeddings

* Integrated Pinecone vector database

* Implemented contract upload and parsing

* Defined AI agent roles (Legal, Compliance, Finance, Operations)

* Tested the system on sample contracts

**Technical Implementation:**

**Vector Database:**
Pinecone was used to store and retrieve contract embeddings efficiently.

**Language Model:**
The gemma-2b-it model powered clause interpretation.

**Embedding Model:**
all-MiniLM-L6-v2 was used to generate vector representations.

**Data Pipeline:**

* Input: 510 contract text files from full_contract_txt

* Processing: Text split into overlapping chunks using LangChain

* Embedding: Chunks converted into vectors

* Storage: Stored in Pinecone

* Retrieval: 20 RAG context files generated

**Multi-Agent Analysis Summary**
| Domain     | Focus Area                                    | Risk Level | Confidence |
| ---------- | --------------------------------------------- | ---------- | ---------- |
| Compliance | Privacy laws & regulatory rules               | High       | 1.0        |
| Finance    | Payments, reimbursements, billing             | Medium     | 0.7        |
| Operations | Deliverables, SLAs, execution duties          | Medium     | 0.8        |
| Legal      | IP rights, termination clauses, governing law | Low        | 0.85       |

**Key Clause Findings**

Compliance:
Confidential data must not be shared with external parties without written approval.

Finance:
Service recipients must cover costs such as licensing and subcontractor fees.

Operations:
Specific parties are responsible for marketing approvals and product fulfillment.

Legal:
Termination requires written notice explaining the reasons and default conditions.

**Challenges Faced:**

* Large models (Qwen2.5, Mistral-7B) exceeded 16GB RAM limits

* Switched to Gemma-2B-IT for better compatibility

* Used API-based embeddings instead of local models
