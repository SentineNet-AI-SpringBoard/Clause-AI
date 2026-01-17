#### CLAUSE AI – Milestone 2
----
Multi-Agent Coordination, LangGraph Orchestration & Collaborative Reasoning

----

#### Milestone Objective
----
Introduce coordination logic and graph-based orchestration to intelligently route queries, execute only relevant agents, maintain shared state, and enable collaborative multi-agent reasoning.

----

#### Coordinator Logic (Rule-Based Routing)
----
- Introduced a **Coordinator** to route queries to the correct agents  
- Avoided unnecessary execution of all agents  
- Collected structured outputs from relevant agents  

**Key Concepts:**
- Keyword-based routing rules  
- Dynamic agent selection  
- Unified coordinator output  

**Student Task:**
- Add keyword: `indemnity`  
- Decide responsible agent  
- Test routing behavior  

----

#### Why Coordinator is Needed?
----
- Agents and coordinator are **not the same**  
- Agents perform **domain-specific analysis**  
- Coordinator manages **decision-making, routing, and aggregation**  
- Improves efficiency, scalability, and clarity  

----

#### LangGraph Basics
----
- Learned nodes, edges, and shared state  
- Built first LangGraph pipeline  
- Executed agents via graph flow  
- Inspected outputs and execution order  

**Student Task:**
- Change agent execution order  
- Add debug logs  
- Observe output changes  

----

#### Multi-Agent Graph (Nodes & Edges)
----
- Added all agents as LangGraph nodes  
- Maintained shared execution state  
- Executed agents sequentially  

**Capabilities:**
- Modular agent execution  
- Shared state propagation  
- Controlled execution flow  

**Student Task:**
- Remove an agent  
- Change execution order  
- Observe state evolution  

----

#### Conditional Routing in LangGraph
----
- Introduced conditional edges  
- Dynamically executed only relevant agents  
- Improved performance and relevance  

**Test Scenarios:**
- Single-intent queries  
- Finance-only queries  
- Multi-intent queries (limitations observed)  

**Student Task:**
- Add new keyword mappings  
- Test multiple queries  
- Observe agent selection  

----

#### Conversation Memory & State Persistence
----
- Added memory to shared graph state  
- Enabled agents to read previous outputs  
- Supported multi-step reasoning  

**Outcomes:**
- Persistent reasoning context  
- Traceable agent decisions  
- Ordered memory accumulation  

----

#### Agent-to-Agent Communication & Validation
----
- Enabled agents to read shared memory  
- Added cross-agent validation logic  
- Refined outputs collaboratively  

**Example:**
- Finance agent validates compliance findings  
- Legal agent performs final validation  

**Student Task:**
- Let Operations agent read Legal output  
- Add SLA enforceability validation  

----

#### Compliance Pipeline
----
- Built end-to-end compliance pipeline  
- Chained retrieval → analysis → validation  
- Generated structured compliance risk output  

**Student Task:**
- Change retrieval keywords  
- Compare extracted clauses and confidence  

----

#### Finance Pipeline
----
- Extracted payment & penalty clauses  
- Generated finance-specific risk summary  

**Student Task:**
- Add keyword `interest`  
- Observe changes in risk level  

----

#### Legal Pipeline
----
- Extracted legal clauses at scale  
- Produced structured legal analysis  

**Student Task:**
- Add keyword `indemnification`  
- Observe clause increase  

----

#### Operations Pipeline
----
- Extracted operational obligations  
- Identified timelines, SLAs, and deliverables  
- Assessed execution risk  

**Student Task:**
- Add keyword `uptime`  
- Compare extracted obligations  

----

#### Coordinator: Merging Agent Outputs
----
- Merged outputs from all pipelines  
- Produced unified JSON structure  
- Prepared system for parallel execution  

**Enhancements:**
- Overall risk computation  
- Confidence aggregation  
- Highest-risk clause identification  

**Student Task:**
- Implement confidence aggregation  
- Print highest-risk clause  

----

#### Milestone-2 Summary
----
- Introduced intelligent query routing  
- Implemented LangGraph-based orchestration  
- Enabled conditional execution of agents  
- Added shared memory and collaboration  
- Built domain-specific pipelines  
- Prepared foundation for scalable, parallel multi-agent reasoning  

> **Milestone 2 transforms isolated agents into a coordinated, stateful, and intelligent contract analysis system.**
----
