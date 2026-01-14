Project Overview: ClauseAI Contract Analysis System
This repository contains a multi-stage pipeline designed to automate the extraction and analysis of key provisions within legal contracts. By leveraging a multi-agent architecture, the system provides structured insights into legal risks and financial obligations


Project Architecture
The project is organized into two primary milestones that move from raw data preparation to autonomous AI analysis.

Milestone 1: Data Preparation and Exploratory Analysis
The foundation of the project focused on transforming unstructured legal documents into a format suitable for machine learning models.

Data Preprocessing: Implemented Python-based cleaning scripts to standardize text, remove noise (special characters and inconsistent whitespace), and handle encoding issues.

Exploratory Data Analysis (EDA): Performed statistical analysis on the contract corpus to identify common legal terminology and document structures.

Objective: Ensuring high data integrity to prevent "garbage-in, garbage-out" scenarios during the inference phase.

Milestone 2: Multi-Agent Orchestration
The second phase involved building a sophisticated "brain" for the system using LangGraph and specialized AI agents.

Central Orchestrator: Developed a routing logic that acts as a project manager, distributing specific contract sections to the appropriate subject matter experts.

Specialized Agents: Defined distinct roles for a Legal Agent (focused on liability and risk) and a Financial Agent (focused on payment terms and fiscal obligations).

State Management: Utilized a graph-based workflow to allow agents to share context and refine their findings before producing a final report.

Output: The system generates a comprehensive final_contract_analysis.json file, providing a structured summary of all identified clauses.
