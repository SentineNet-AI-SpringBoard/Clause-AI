# Deploy (Single Docker Service)

This repo contains:
- **FastAPI backend**: `milestone3/backend` (runs on port `8000` inside the container)
- **Streamlit UI**: `milestone4/UI/UI` (runs on port `$PORT` / `8501`)

The Docker setup runs **both** in one container.

## 1) Build + run locally (Docker Desktop)

From repo root:

```bash
docker build -t clauseai:local .

# Streamlit will be on http://localhost:8501
# FastAPI will be on http://localhost:8000 (internal, but also reachable locally)
docker run --rm -p 8501:8501 -p 8000:8000 \
  -e OPENAI_API_KEY="..." \
  -e PINECONE_API_KEY="..." \
  -e PINECONE_ENV="..." \
  clauseai:local
```

## 2) Deploy to a single-service platform (Render/Fly/Azure)

Use the Dockerfile at repo root.

### Required environment variables

- `OPENAI_API_KEY` (if using OpenAI in the pipeline)
- `PINECONE_API_KEY` / `PINECONE_ENV` (if using Pinecone)
- `PORT` (provided automatically by many platforms; Streamlit will bind to it)

### Notes

- UI talks to backend via `BACKEND_URL` (defaults to `http://127.0.0.1:8000` inside the container).
- This Docker image forces **CPU-only torch** via `deploy/requirements-docker.txt` to avoid huge CUDA/NVIDIA wheels.

## 3) Health check / URLs

- UI: `http://<host>/` (Streamlit)
- Backend (optional): `http://<host>:8000/docs` if you expose it separately.
