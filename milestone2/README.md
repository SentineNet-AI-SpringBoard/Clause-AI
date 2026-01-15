Milestone 2: Multi-Agent Orchestration
This folder contains the core logic for the ClauseAI agentic system. The goal of this milestone was to move beyond simple text processing and create a team of AI agents that can analyze contracts collaboratively.

Contents
1. Static Orchestrator (main_orchestrator.py)
This was the initial version of our system. It uses a fixed workflow to route contract sections to Legal and Finance agents based on predefined rules. It is a reliable way to handle standard, predictable documents.

2. Dynamic Controller (dynamic_orchestrator.py)
This is the upgraded version of the system. Instead of following a fixed path, it uses a central "Controller" to manage the workflow in real-time.

Signal-Based Routing: The controller monitors the output of each agent. If a "High Risk" signal is detected, it automatically routes the task to a Compliance or Legal expert.

Memory Management: It is designed to check for existing analysis in a vector database (Pinecone) to avoid redundant processing.

Adaptive Logic: The system can change its plan during execution based on the specific content it finds within a contract.

3. Agent Configurations (agents_setup.py)
This file contains the personas and system prompts for our specialized agents, ensuring they maintain a professional and focused tone during analysis.
