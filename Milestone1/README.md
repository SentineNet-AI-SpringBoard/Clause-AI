Milestone 1: Project Planning, Setup & Exploratory Data Analysis

1. Environment Setup

    i. Python environment configuration

    ii. Installation of required libraries:

        i. LangChain

        ii. LangGraph

        iii. Pinecone

        iv. Data processing libraries (NumPy, Pandas, Matplotlib, etc.)

    iii. Folder structure creation for datasets, processed files, chunks, and embeddings


2. Dataset Understanding & Loading

    i. contract dataset (CUAD-style legal contracts) loaded:

        i. folder of raw contract text files
        ii. json file
        iii. master_clauses.csv


3. Exploratory Data Analysis (EDA)

Performed EDA on the contract text corpus without modifying or cleaning the data.

Key analyses include:

    i. Number of contract files

    ii. Distribution of contract sizes and lengths

    iii. Word count statistics per contract

    iv. Identification of empty or missing files

    v. Detection of null or malformed entries

    vi. Frequency analysis of common legal terms

Visualizations created:

    i. Histogram of contract lengths

    ii. Boxplot of text length distribution

    iii. Bar chart of top legal keywords

    iv. Scatter plot of file size vs word count


4. Text Cleaning & Normalization

Operations performed:

    i.Removal of page headers and footers

    ii. Whitespace normalization

    iii. Removal of repeated line breaks

    iv. Removal of noisy characters (tabs, non-ASCII symbols)

    v. Fixing hyphenation across line breaks

    vi. Standardizing casing while preserving section headers

    vii. Retaining structural markers such as clause headings

    viii. Cleaned files were saved as new transformed files, preserving original raw data.


5. Sentence Splitting & Chunking

    i. Cleaned contract text was split into manageable chunks

    ii. Chunk size and overlap were configured to preserve context

    iii. Sentence boundaries were maintained

    iv. Chunked outputs were stored as structured JSON files

This step prepares the data for embedding and retrieval.


6. Embedding Preparation & Vectorization

    i. Chunk embeddings were generated using an embedding model

    ii. Vectors were normalized for cosine similarity

    iii. Embeddings were stored locally in structured JSON format

    iv. Embedding statistics and dimensional checks were performed

This step enables semantic search and retrieval in later stages.


7. Pinecone Vector Database Setup

    i. Pinecone client initialization

    ii. Vector index creation

    iii. Upsert of embedded contract chunks

    iv. Verification of stored vectors

    v. Semantic search testing using sample queries

    vi. Visualization of similarity score distributions


8. Agent-Level Analysis

    i. Definition of a standard agent output schema

    ii. Creation of individual agent logic for domain analysis

    iii. Execution of domain-specific analysis for:

        i. Legal Agent

        ii. Compliance Agent

        iii. Finance Agent

        iv. Operations Agent 

Each agent produced structured JSON outputs containing:

    i. Extracted clauses

    ii. Risk assessment

    iii. Confidence scores

    iv. Evidence references

These outputs serve as inputs for coordination and orchestration in Milestone 2.