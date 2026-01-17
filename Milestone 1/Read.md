# CLAUSE AI – Milestone 1
### Project Planning, Environment Setup & Exploratory Data Analysis

---

### Overview

CLAUSE AI is a contract intelligence system aimed at analyzing legal agreements, structuring contractual knowledge, and enabling semantic understanding of clauses using modern NLP techniques. The project is designed as a foundation for a scalable Retrieval-Augmented Generation (RAG) and multi-agent reasoning system for legal documents.

This repository documents Milestone 1, which focuses on establishing the technical groundwork required for advanced contract analysis. The milestone covers dataset understanding, exploratory data analysis, text normalization, sentence-aware chunking, and embedding generation to prepare contracts for downstream semantic retrieval and reasoning.

---

### Objectives of Milestone 1

The primary goal of this milestone is to build a clean, well-structured, and analyzable dataset pipeline that ensures reliability and consistency before introducing complex agent-based reasoning.

**Key objectives include:**

- Setting up a reproducible project structure and Python environment  
- Understanding the characteristics and variability of contract documents  
- Performing exploratory data analysis to uncover patterns and anomalies  
- Cleaning and normalizing contract text while preserving legal meaning  
- Splitting documents into sentence-aware overlapping chunks  
- Generating and validating vector embeddings for semantic representation  

---


### Technology Stack

#### Programming Language
- Python 3.1.1.9

#### Libraries and Tools
- Pandas – Data manipulation and analysis  
- NumPy – Numerical operations  
- Matplotlib – Visualization for EDA and validation  
- LangChain – Text splitting and NLP utilities  
- Pinecone Client – Vector database integration (future stages)  
- PyPDF2 / python-docx – Document parsing  
- Jupyter Notebook – Experimentation and milestone documentation  

---

### Dataset Understanding & Exploratory Data Analysis

Exploratory Data Analysis (EDA) was performed to gain a clear understanding of the contract corpus before applying any transformations or modeling.

#### EDA Objectives
- Analyze the distribution of contract lengths and sizes  
- Measure word count variability across contracts  
- Identify frequently occurring legal and contractual terms  
- Detect missing, empty, or corrupted contract files  

#### Key Analyses Performed
- Word count per contract  
- File size versus word count correlation  
- Frequency analysis of legal keywords  
- Identification of empty or invalid documents  

#### Visualizations
- Histogram of contract lengths  
- Boxplot showing text length distribution  
- Bar chart of top 20 most frequent legal keywords  
- Word cloud representing common clause terms  
- Scatter plot of file size versus word count  

All analysis, plots, and observations are documented in:

notebooks/Milestone1_ProjectPlanning_Setup_EDA.ipynb


---

### Text Cleaning and Normalization

Text preprocessing in this milestone focuses strictly on formatting improvements, ensuring that the semantic meaning of legal clauses remains unchanged.

#### Cleaning Steps Applied
- Removal of page headers and footers  
- Whitespace normalization  
- Removal of excessive or repeated line breaks  
- Cleaning of noisy characters (tabs, bullets, non-ASCII symbols)  
- Fixing broken hyphenation across lines  

**Example:**  
termi\nnation → termination



- Standardization of casing while preserving original structure  
- Preservation of section headers such as:
  - TERMINATION  
  - CONFIDENTIALITY  
  - GOVERNING LAW  

#### Output Format
data/transformed/{contract_id}_cleaned.txt



---

### Sentence-Aware Chunking Strategy

To enable efficient embedding generation and semantic retrieval, cleaned contracts are split into overlapping chunks while respecting sentence and paragraph boundaries.

#### Chunk Configuration
- Chunk size: 1000 characters  
- Overlap: 200 characters  
- Boundary-aware splitting using sentence and paragraph separators  

#### Implementation Approach
Chunking is performed using `RecursiveCharacterTextSplitter` with prioritized separators to maintain contextual integrity.

#### Output Structure
data/chunks/
├── contract_001_chunks.json
├── contract_002_chunks.json
└── ...



#### Validation Checks
- Chunk length distribution analysis  
- Overlap consistency verification  

---

### Embeddings and Vector Processing

Each chunk is converted into a dense vector embedding to enable semantic understanding and similarity-based retrieval.

#### Steps Performed
- Load chunked contract files  
- Generate embeddings for each chunk  
- Store embeddings locally in JSON format  
- Process the first 20 contracts for demonstration and validation  

#### Directory Layout
data/
├── chunks/
│ └── contract_001_chunks.json
│
└── embeddings/
└── contract_001_embeddings.json


#### Quality and Sanity Checks
- Verification of embedding vector dimensions  
- Visualization of embedding norm distribution  
- Similarity checks using:
  - Cosine similarity  
  - Dot product comparison  

These checks ensure numerical stability and semantic consistency of the generated vectors.

---

### Notebook Summary

**Notebook:**  
`Milestone1_ProjectPlanning_Setup_EDA.ipynb`

#### Contents
- Dataset inspection and EDA  
- Text cleaning and normalization pipeline  
- Sentence-aware chunking implementation  
- Embedding generation workflow  
- Visual validations and sanity checks  

This notebook serves as the complete technical record for Milestone 1.

---
