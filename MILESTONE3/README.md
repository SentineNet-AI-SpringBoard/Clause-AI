Milestone 3 - Documentation

1. Milestone 3 - Objectives:
    1. Implement Parallel Processing for multi-domain clause extraction.
    2. Develop structured pipelines for compliance and financial risk identification.
    3. Test multi-turn interaction between domain-specific agents.
    4. Store intermediate results in Pinecone for quick retrieval.

2. Technical Implementations:
    1. Milestone3.ipynb Notebook:
        1. Connected to Pinecone - index name "clauseai-agents" - store the refined agent outputs.
        2. Used Model - "gemma2:9B" for analysis.
        3. Done cross-agent refinement to enhance the risk levels.
        4. Generated final JSON output file.
        5. Generated template for Human-readable Risk Analysis.
    3. app.py:
        1. Connected to the Milestone 3 as the output directory.
        2. Fastapi - HTTP request and responses.
        3. Pydantic - Converts JSON to structured data.
        4. Uvicorn - ASGI - run FastAPI applications.

3. Cross-Agent Refinement:
    1. Legal Risk - before refinement "low" ---> after refinement "medium".
    2. Finance and Operations Risk - before refinement "medium" ---> after refinement "high".
    3. Compliance Risk - initially "high".
    4. Risk Escalations were found and generated.
5. Outcomes:
   1. Milestone3.ipynb Notebook:
        1. Parallel Execution completed successfully.
        2. Created shared memory for all agents.
        3. Cross-Agent Refinement done and Risks enhanced for all agents done.
        4. Final JSON output and Human-Readable Ouput Template generated.
   3. app.py
        1. Connected to milestone 3 notebook as output directory.
        2. Deployed the website - working properly
        3. Using Postman API tested for - health, rootends, validated, short contract,invalid entry etc
