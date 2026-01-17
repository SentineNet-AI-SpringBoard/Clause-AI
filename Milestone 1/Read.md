CLAUSE AI – Milestone 1
Project Planning, Setup & Exploratory Data Analysis

📌 Project Overview
CLAUSE AI is a contract intelligence system focused on analyzing legal agreements, extracting structured knowledge, and enabling semantic search over clauses using embeddings.

This repository contains Milestone 1, which covers:

Project setup
Dataset understanding
Exploratory Data Analysis (EDA)
Text cleaning & normalization
Sentence-aware chunking with overlap
Embedding generation & validation

📁 Project Structure
 
CLAUSE_AI/
│
├── Artifacts/ # Generated plots, figures, reports
├── app/ # Future Streamlit / API app
├── data/
│ ├── raw/ # Original datasets
│ │ ├── full_contract_txt/
│ │ ├── CUAD_V1.json
│ │ └── master_clauses.csv
│ │
│ └── transformed/ # Cleaned & processed text
│
├── notebooks/
│ └── Milestone1_ProjectPlanning_Setup_EDA.ipynb
│
├── env/ # Python virtual environment
├── requirements.txt
└── README.md

Requirements
 
pinecone-client>=2.2.1
PyPDF2>=3.0.0
python-docx>=0.8.11
streamlit>=1.24.0
fpdf2>=2.6.0
pandas>=1.5.0
tqdm>=4.64.0
requests>=2.28.0


📊 Dataset Understanding & EDA
Objectives
Understand contract size and structure
Analyze text length distribution
Identify frequent legal terms
Detect missing or empty files
Key Analyses
Word count per contract
File size vs word count correlation
Most common legal keywords
Empty or corrupted document detection
Visualizations
📈 Histogram – contract length
📦 Boxplot – text length distribution
☁️ WordCloud – frequent clause terms
📊 Bar chart – top 20 keywords
🔵 Scatter plot – file size vs word count
All EDA work is documented in:

 
notebooks/Milestone1_ProjectPlanning_Setup_EDA.ipynb


🧹 Text Cleaning & Normalization
The goal is formatting improvement only, without changing meaning.

Cleaning Steps Applied
Remove page headers and footers
Normalize whitespace
Remove excessive line breaks
Clean noisy characters (tabs, bullets, non-ASCII)
Fix broken hyphenation across lines
(e.g., termi\nnation → termination)
Standardize casing (original structure preserved)
Preserve section headers like:

 
TERMINATION
CONFIDENTIALITY
GOVERNING LAW

Output Format
 
data/transformed/{contract_id}_cleaned.txt


---> Sentence-Aware Chunking Strategy
Chunk Configuration
Chunk size: 1000 characters
Overlap: 200 characters
Boundary-aware: Sentence and paragraph level
Chunking Logic
Uses RecursiveCharacterTextSplitter with separators:

 

Output Structure
 
data/chunks/
├── contract_001_chunks.json
├── contract_002_chunks.json
└── ...

Validations
Chunk length distribution
Overlap consistency check

---> Embeddings & Vector Processing
Steps Performed
Load chunked contract files
Generate embeddings for each chunk
Store vectors locally in JSON format
Process first 20 contracts for demo
Directory Layout
 
data/
├── chunks/
│ └── contract_001_chunks.json
│
└── embeddings/
└── contract_001_embeddings.json

Quality Checks
Vector dimension verification
Embedding norm distribution visualization
Similarity sanity checks:

Cosine similarity
Dot product comparison

---> Notebook Summary
File:
Milestone1_ProjectPlanning_Setup_EDA.ipynb

Contains:

EDA
Text cleaning pipeline
Chunking logic
Embedding generation
Visual validations
Sanity checks
