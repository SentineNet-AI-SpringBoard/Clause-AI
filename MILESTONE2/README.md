Milestone 2 
1. Objective

Build a Planning Module capable of creating and managing multiple specialized AI agents.

Integrate APIs to enable contract uploading and automatic domain classification.

Create structured prompt templates to support effective agent-to-agent interaction.

Verify and test inter-agent workflows using the LangGraph framework.

2. Technical Implementation

Utilized LangGraph to design, manage, and validate communication between agents.

Developed a module to instantiate and coordinate domain-specific agents, including Legal, Compliance, Finance, and Operations.

Implemented model-based routing using gemma2:9B to direct queries intelligently.

Retrieved contextual and analytical data from Pinecone vector storage.

Enabled sequential execution combined with conditional routing to optimize processing flow.

3. Agent Shared Memory and Communication

Implemented a GraphState with persistent memory to maintain shared context across agent nodes.

The Compliance Agent evaluates potential risks and records findings in shared memory.

The Finance Agent accesses this memory to assess financial implications or penalties.

The Legal Agent performs final verification and updates the shared memory with validation results.

Ensured smooth agent-to-agent communication through shared state management.

4. Outcome

Successfully loaded pre-processed contract insights from Pinecone, including total contracts analyzed and clauses extracted per agent.

Computed a Confidence Aggregate and Confidence Range, identifying the highest-risk clause across all domains.

Achieved approximately 75% reduction in execution time by using conditional routing to bypass unnecessary agents.

Generated comprehensive system metrics such as total queries processed, average agents invoked per query, and average clauses retrieved.

Produced a consolidated final risk assessment report, including recommendations and overall pipeline validation status.
