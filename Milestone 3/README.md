Milestone 3 - Documentation

1. Milestone 3 - Objectives:


a) Implement Parallel Processing for multi-domain clause extraction.

b) Develop structured pipelines for compliance and financial risk identification.

c)Test multi-turn interaction between domain-specific agents.

d)Store intermediate results in Pinecone for quick retrieval.

2. Technical Implementations:

i) Milestone3.ipynb Notebook:
Connected to Pinecone - index name "clauseai-agents" - store the refined agent outputs.

Used Model - "gemma2:9B" for analysis.

Done cross-agent refinement to enhance the risk levels.

Generated final JSON output file.

Generated template for Human-readable Risk Analysis.

ii) app.py:
Connected to the Milestone 3 as the output directory.

Fastapi - HTTP request and responses.

Pydantic - Converts JSON to structured data.

Uvicorn - ASGI - run FastAPI applications.

3. Cross-Agent Refinement:

Legal Risk - before refinement "low" ---> after refinement "medium".

Finance and Operations Risk - before refinement "medium" ---> after refinement "high".

Compliance Risk - initially "high".

Risk Escalations were found and generated.

4. Outcomes:

i) Milestone3.ipynb Notebook:

Parallel Execution completed successfully.

Created shared memory for all agents.

Cross-Agent Refinement done and Risks enhanced for all agents done.

Final JSON output and Human-Readable Ouput Template generated.

ii) app.py
Connected to milestone 3 notebook as output directory.

Deployed the website - working properly

Using Postman API tested for - health, rootends, validated, short contract,invalid entry etc
