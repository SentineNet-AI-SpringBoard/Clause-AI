MILESTONE 2 - DOCUMENTATION

Coordinator Logic & Query Routing

This phase introduced a rule-based Coordinator to manage how user queries are routed to the correct analysis agents. Instead of running all agents for every query, the coordinator inspects query keywords and decides which agents are relevant (Legal, Compliance, Finance, Operations). This improves efficiency, keeps outputs focused, and mirrors how real review teams route issues to the right domain experts. The coordinator also collects and merges structured agent outputs into a unified response.

LangGraph-Based Agent Orchestration

LangGraph was used to model agents as nodes in a graph with explicit execution flow. Each agent operates on a shared state, allowing information to move cleanly through the pipeline. Initial graphs followed a simple sequential order, which was later modified to test different execution paths and agent removal. This helped demonstrate how execution order affects outputs and how flexible graph-based orchestration supports controlled multi-agent workflows.

Conditional Routing & State Persistence

Conditional routing was added to ensure that only relevant agents run based on the query intent. For example, legal-only queries trigger only the Legal agent, while mixed queries activate multiple agents. The graph state was extended with a shared memory component so agents could store and read previous findings. This enabled multi-step reasoning, traceability of decisions, and better coordination across agents without duplicating work.

Agent Collaboration & Unified Outputs

Agent-to-agent communication was implemented using shared memory and validation notes. Agents could review findings from earlier agents, flag conflicts, and add context-aware observations. Separate pipelines were built for Compliance, Finance, Legal, and Operations, each chaining retrieval, analysis, and validation. Finally, the Coordinator merged all pipeline outputs into a single structured JSON response, computed overall risk indicators, and prepared the system for parallel and scalable execution in future milestones.