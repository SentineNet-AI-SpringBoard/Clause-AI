MILESTONE 1 - DOCUMENTATION
Project Setup & Foundation

In this milestone, the focus was on setting up a stable and well-structured development environment for CLAUSE AI. A clear project folder structure was created, along with a virtual environment and dependency management to ensure consistent execution across systems. The setup supports further development of data pipelines, retrieval systems, and agent-based analysis in a controlled and repeatable manner.

Contract Data Understanding & Preparation

A dataset of 510 contract text files was loaded and reviewed to understand its size, structure, and quality. Basic exploratory data analysis was performed to study contract lengths, word counts, common legal terms, and missing or empty files. Contracts were then cleaned to improve formatting by removing noise, fixing line breaks and hyphenation issues, and standardizing spacing, while keeping the original legal meaning and section structure intact.

Chunking, Embeddings & Semantic Search

Cleaned contracts were split into overlapping text chunks to preserve context across sections. Each chunk was converted into vector embeddings and stored in Pinecone, enabling semantic search over the contract data. Retrieval quality was checked using similarity scores and basic validation plots to confirm that relevant contract sections were being returned for analysis.

Multi-Agent Contract Analysis

A simple but structured multi-agent framework was built to analyze contracts from different perspectives. Separate agents for Legal, Compliance, Finance, and Operations were created using a shared base design and common output format. Each agent reviewed retrieved contract content to extract relevant clauses, assess risk levels, and provide confidence scores supported by evidence. Initial results showed that this approach can consistently identify key risks and obligations across contracts and serves as a strong base for future expansion.


