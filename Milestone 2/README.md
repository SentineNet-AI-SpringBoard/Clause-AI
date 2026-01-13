Milestone 2 - Documentation

1. Objective
    1. Develop the Planning Module to generate and coordinate specialized agents
    2. Implement API integration for contract upload and domain classification.
    3. Design basic prompt templates for agent communication.
    4. Validate inter-agent coordination using LangGraph.
2. Technical Implementations
    1. LangGraph to design and validate inter-agent coordination.
    2. Module to generate and coordinate specialized agents - Legal, Compliance, Finance, and Operations.
    3. Keyword-Based Routing
    4. Sequential Execution along with Conditional Routing.
3. Agent Shared Memory and Communication Details
    1. GraphState with Memory - presist data across agent nodes.
    2. Compliance Agent analyse the risk and adds it to memory.
    3. Finance Agent reads this for any extra penalities.
    4. Legal Agent - Final validation and writes to the shared memory.
    5. Agent to Agent Communication.
4. Outcome
    1. Loads pre-computed results from JSON files for each agent, reporting total contracts analyzed and total clauses extracted.
    2. Calculates a Confidence Aggregate and Confidence Range for the analysis - identifies the Highest-Risk Clause across all agent domains.
    3. Conditional routing can save approximately 75% of execution time compared to sequential processing by skipping irrelevant agents.
    4. Overall statistics - total queries processed, average agents routed per query, and average clauses retrieved.
    5. Generates a final risk summary including recommendations and validation status for pipelines.
