Milestone 2 - Documentation


Objective
Develop the Planning Module to generate and coordinate specialized agents
Implement API integration for contract upload and domain classification.
Design basic prompt templates for agent communication.
Validate inter-agent coordination using LangGraph.


Technical Implementations
LangGraph to design and validate inter-agent coordination.
Module to generate and coordinate specialized agents - Legal, Compliance, Finance, and Operations.


Keyword-Based Routing
Sequential Execution along with Conditional Routing.
Agent Shared Memory and Communication Details


GraphState with Memory - presist data across agent nodes.
Compliance Agent analyse the risk and adds it to memory.
Finance Agent reads this for any extra penalities.
Legal Agent - Final validation and writes to the shared memory.
Agent to Agent Communication.


Outcome


Loads pre-computed results from JSON files for each agent, reporting total contracts analyzed and total clauses extracted.

Calculates a Confidence Aggregate and Confidence Range for the analysis - identifies the Highest-Risk Clause across all agent domains.

Conditional routing can save approximately 75% of execution time compared to sequential processing by skipping irrelevant agents.

Overall statistics - total queries processed, average agents routed per query, and average clauses retrieved.

Generates a final risk summary including recommendations and validation status for pipelines.
