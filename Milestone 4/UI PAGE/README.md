# Milestone 4 — UI (Streamlit)

This UI calls the Milestone 3 FastAPI backend.

## 1) Start the backend

```powershell
cd backend
python -m uvicorn app:app --reload

```

## 2) Start the UI

```powershell
cd milestone4\UI\UI
pip install -r requirements.txt

# Optional: point UI to a different backend base URL
set BACKEND_URL=http://127.0.0.1:8000

cd "UI PAGE"
streamlit run app.py
```

## Login + history

- Authentication and analysis history are stored in the **backend SQLite DB** (not in the UI).
- After login, every Ask / Launch Analysis run is saved automatically.
- Use the sidebar **Recent Analyses** or the **History** page to reopen a previous run.

## What gets sent to the backend

- Uploads are sent as real files to `POST /analyze` (multipart form-data).
- The question box is passed as `question`.
- UI tone options are mapped to backend tones (`executive` or `simple`).

