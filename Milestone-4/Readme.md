
# Milestone 4 — Streamlit UI

## Overview

This milestone implements a **Streamlit-based UI** that connects to the **Milestone 3 FastAPI backend** for contract analysis.

---

## Run Instructions

### Start Backend

```bash
uvicorn app:app --reload --port 8000
```

### Start UI

```bash
pip install -r requirements.txt
streamlit run app.py
```

(Optional)

```bash
set BACKEND_URL=http://127.0.0.1:8000
```

---

## Features

* File upload and question-based analysis
* Login and analysis history (stored in backend SQLite DB)
* View and reopen previous analyses
* UI tone mapped to backend response style

---

## Notes

* Files are sent to `POST /analyze` as multipart data
* Question input is passed as `question`
* UI remains stateless; backend handles persistence

---

## Author

**Anjali More**

---

