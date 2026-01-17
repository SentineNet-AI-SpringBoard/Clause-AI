CLAUSE AI – Milestone 1


Project Planning, Setup & Exploratory Data Analysis
Project Overview
CLAUSE AI is a contract intelligence system designed to analyze legal agreements, extract structured
information from contractual clauses, and enable semantic search using vector embeddings. The long-term
goal of this project is to build a scalable retrieval-augmented generation (RAG) pipeline for legal document
understanding.
This repository documents Milestone 1 of the project, which focuses on setting up the development
environment, understanding the dataset, performing exploratory data analysis (EDA), and preparing
contracts for downstream NLP tasks.
Milestone 1 covers the following components:
• Project directory and environment setup
• Dataset inspection and understanding
• Exploratory Data Analysis (EDA)
• Text cleaning and normalization
• Sentence-aware chunking with overlap
• Embedding generation and validation
Project Structure
The repository follows a modular and scalable structure to separate raw data, processed artifacts,
notebooks, and application code.
CLAUSE_AI/
 Artifacts/ – Generated plots, figures, and reports
 app/ – Placeholder for future Streamlit or API application
 data/
     raw/ – Original datasets
       full_contract_txt/
       CUAD_V1.json
       master_clauses.csv
     transformed/ – Cleaned and normalized contracts
 notebooks/
     Milestone1_ProjectPlanning_Setup_EDA.ipynb
 env/ – Python virtual environment
 requirements.txt
 README.md
 
Dependencies


The project relies on commonly used libraries for NLP, data analysis, embeddings, and visualization. All
dependencies are listed in requirements.txt.
• pinecone-client
• PyPDF2
• python-docx
• streamlit
• fpdf2
• pandas
• tqdm
• requests


Dataset Understanding and EDA


Exploratory Data Analysis was performed to gain insights into the size, structure, and quality of the contract
corpus before applying any NLP transformations.
EDA Objectives:
• Understand variation in contract length and structure
• Analyze text length and word count distribution
• Identify frequently occurring legal terms
• Detect missing, empty, or corrupted contract files
Key Analyses and Visualizations:
• Word count per contract
• File size versus word count correlation
• Top legal keywords across contracts
• Histogram of contract lengths
• Boxplot of text length distribution
• Scatter plot of file size versus word count
All EDA steps, plots, and observations are documented in the notebook
Milestone1_ProjectPlanning_Setup_EDA.ipynb.
Text Cleaning and Normalization
Text preprocessing focuses strictly on formatting improvements without altering the semantic meaning of
legal clauses. Structural information is preserved to support clause-level retrieval.

Cleaning steps applied:

• Removal of page headers and footers
• Whitespace normalization
• Removal of excessive or repeated line breaks
• Cleaning of noisy characters such as tabs, bullets, and non-ASCII symbols
• Fixing broken hyphenation across lines
• Standardization of casing while preserving original structure
• Preservation of section headers such as TERMINATION and CONFIDENTIALITY
Cleaned contracts are stored in the following format: data/transformed/{contract_id}_cleaned.txt

Sentence-Aware Chunking Strategy

To enable efficient embedding and retrieval, cleaned contracts are split into overlapping text chunks while
respecting sentence and paragraph boundaries.
• Chunk size: 1000 characters
• Chunk overlap: 200 characters
• Boundary-aware splitting using RecursiveCharacterTextSplitter
Chunk files are stored as JSON objects under data/chunks/ for each contract.

Embeddings and Vector Processing

Each text chunk is converted into a vector embedding using a language model. For demonstration and
validation purposes, embeddings were generated for the first 20 contracts.
Quality checks performed:
• Embedding vector dimension verification
• Visualization of embedding norm distribution
• Similarity sanity checks using cosine similarity and dot product


Notebook Summary


The notebook Milestone1_ProjectPlanning_Setup_EDA.ipynb serves as the central documentation of this
milestone and includes EDA, preprocessing pipelines, chunking logic, embedding generation, visual
validations, and sanity checks
