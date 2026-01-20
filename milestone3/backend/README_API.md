# Milestone 3 — FastAPI Backend

This backend wraps the Milestone 3 contract analysis pipeline into an API.

## Run locally

From the workspace root:

```bash
pip install -r requirements.txt
```

Then:

```bash
cd milestone3/backend
uvicorn app:app --reload --port 8000
```

If your UI runs on a different port/origin, set allowed CORS origins:

```bash
set FRONTEND_ORIGINS=http://localhost:5173,http://localhost:3000
```

Open docs:
- http://127.0.0.1:8000/docs

## Analyze endpoint

`POST /analyze` (multipart form-data)
- `file`: contract file (`.txt`, `.pdf`, `.docx`)
- `question`: user question
- `tone`: `executive` or `simple`
- `no_evidence_threshold`: float, default `0.25`
- `contract_id`: optional override

If the question has no strong semantic match to the uploaded document, the API returns `no_evidence=true` and does not hallucinate.

## Sample file (for Thunder Client)

Use the included [milestone3/backend/sample_contract.txt](milestone3/backend/sample_contract.txt) as a real upload file when testing `POST /analyze`.

## Thunder Client (free) option

Some Thunder Client installations restrict file uploads. If you cannot send multipart files, use:

`POST /analyze_text` (JSON)

Body (JSON example):

```json
{
	"contract_text": "MASTER SERVICES AGREEMENT\n\n1. Payment Terms: ...",
	"question": "Summarize payment terms and late fees",
	"tone": "executive",
	"no_evidence_threshold": 0.25,
	"contract_id": "uploaded_contract"
}
```

## 10 test cases

```bash
cd milestone3/backend
python test_api.py
```

## Troubleshooting: torch DLL error (WinError 1114)

If you see an error like `OSError: [WinError 1114] ... c10.dll` when importing `torch`/`transformers`, that is a Windows native dependency issue.

Good news: the backend pipeline automatically falls back to a lightweight hashing-based embedder if `sentence-transformers` (and therefore `torch`) cannot be loaded.

If you *do* want to fix PyTorch, common fixes are:
- Install/repair **Microsoft Visual C++ Redistributable 2015–2022**.
- Reinstall PyTorch with the correct build for your machine (CPU vs CUDA) following the official selector: https://pytorch.org/get-started/locally/
