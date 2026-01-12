Milestone 1: Project planning, setup and exploratory data analysis

1. Environment setup
   i. Python environment congiguration
   ii. Installation of required libraries:
       a) Lang chain
       b) Lang graph
       c) Pinecone
       d) Data processing libraries
   iii. Folder structure creation for dataset, processed files, chunks, embeddings
2. Dataset Understanding & Loading
   i. contract dataset (CUAD-style legal contracts) loaded:
       a) folder of raw contract text files
       b)  json file
       c) master_clauses.csv

3. Exploratory Data Analysis (EDA)
   Performed EDA on the contract text corpus without modifying or cleaning the data.
   Key analyses include:
   a) Number of contract files
   b) Distribution of contract sizes and lengths
   c) Word count statistics per contract
   d) Identification of empty or missing files
   e) Detection of null or malformed entries
   f) Frequency analysis of common legal terms

   Visualizations created:
   a) Histogram of contract lengths
   b) Boxplot of text length distribution
   c) Bar chart of top legal keywords
   d) Scatter plot of file size vs word count

4. Text Cleaning & Normalization
   
Operations performed:
a) Removal of page headers and footers
b)  Whitespace normalization
c)  Removal of repeated line breaks
d) Removal of noisy characters (tabs, non-ASCII symbols)
e) Fixing hyphenation across line breaks
f) Standardizing casing while preserving section headers
g) Retaining structural markers such as clause headings
h) Cleaned files were saved as new transformed files, preserving original raw data.

5. Sentence Splitting & Chunking
   a) Cleaned contract text was split into manageable chunks
   b) Chunk size and overlap were configured to preserve context
   c) Sentence boundaries were maintained
   d) Chunked outputs were stored as structured JSON files
This step prepares the data for embedding and retrieval.

7. Embedding Preparation & Vectorization
   a) Chunk embeddings were generated using an embedding model
   b) Vectors were normalized for cosine similarity
    c) Embeddings were stored locally in structured JSON format
   d) Embedding statistics and dimensional checks were performed
This step enables semantic search and retrieval in later stages.

9. Pinecone Vector Database Setup
     a) Pinecone client initialization
    b) Vector index creation
    c) Upsert of embedded contract chunks
    d) Verification of stored vectors
    e) Semantic search testing using sample queries
    f) Visualization of similarity score distributions
   
11. Agent-Level Analysis
     a) Definition of a standard agent output schema
    b) Creation of individual agent logic for domain analysis
    c) Execution of domain-specific analysis for:
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

Readme inside milestone 1
