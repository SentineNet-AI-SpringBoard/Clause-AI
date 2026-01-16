**Objective**

The second milestone focused on building a Planning Module to coordinate specialized AI agents and improve contract analysis efficiency.
Key goals included integrating APIs for contract uploads, enabling domain classification, and validating inter-agent collaboration using LangGraph.

**Key Objectives:**

- Develop a Planning Module to generate and manage specialized agents

- Integrate APIs for contract upload and classification

- Design prompt templates for agent communication

- Validate agent coordination using LangGraph

**Technical Implementations:**

**Multi-Agent Coordination**

- LangGraph used to design and validate agent workflows

- Specialized agents created for:

- Legal

- Compliance

- Finance

- Operations

**Model-Based Routing**

 - gemma2:9B used for intelligent agent routing

- Clauses retrieved from Pinecone for analysis

**Execution Strategy:**

- Sequential execution with conditional routing

- Irrelevant agents are skipped to improve performance

**Agent Shared Memory & Communication:**

**GraphState with Memory**

- Persistent memory across agent nodes

- Stores intermediate analysis results

**Agent Responsibilities**

- Compliance Agent: Analyzes risk and stores findings

- Finance Agent: Checks for penalties and financial risks

- Legal Agent: Performs final validation and updates memory

**Agent-to-Agent Communication**

- Agents read and write to shared memory

- Enables coordinated and consistent analysis

**Outcomes:**

- Loaded pre-computed results from Pinecone

- Reported total contracts analyzed and clauses extracted

**Calculated:**

- Confidence Aggregate

- Confidence Range

- Highest-Risk Clause across domains

- Conditional routing reduced execution time by ~75%

- Generated overall statistics:

   - Total queries processed

  - Average agents routed per query

  - Average clauses retrieved

- Produced final risk summaries with recommendations and validation status
