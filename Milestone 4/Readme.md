# Milestone 4 —  (Streamlit + FastAPI)

Milestone 4 implements a complete end-to-end user interface using Streamlit that integrates with the FastAPI backend developed in Milestone 3. This milestone enables authenticated users to upload files, ask questions, run analyses, and view historical results through a unified UI backed by a persistent database.

---

## System Architecture

- Frontend: Streamlit
- Backend: FastAPI
- Database: SQLite
- Communication Protocol: REST (HTTP)

All authentication, analysis data, and history are stored and managed exclusively by the backend.

---

## Prerequisites

- Python 3.9 or above
- pip package manager
- Milestone 3 backend code available locally

---

## Backend Setup and Execution

The backend must be running before launching the UI.

### Start the Backend

```powershell
cd milestone3\backend
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```
### Start the UI
```powershell
cd milestone4\UI
pip install -r requirements.txt
  # Backend URL Configuration(Optional)
set BACKEND_URL=http://127.0.0.1:8000
streamlit run app.py
```

## Authentication Flow

1.User accesses the Streamlit UI.

2.User logs in using credentials.

3.Login request is sent to the backend authentication endpoint.

4.Backend validates credentials against the SQLite database.

5.On successful authentication, a session is established.

6.The UI uses the authenticated session for all subsequent requests.


## Analysis Workflow

1.Authenticated user uploads one or more files.

2.User enters a question or analysis prompt.

3.User selects the desired response tone.

4.The UI sends the request to the backend using multipart form-data.

5.Backend processes the files and question.

6.Analysis results are returned to the UI.

7.The UI renders the response to the user.


## Backend API Interaction

### Analyze Endpoint

Method: POST

Endpoint: /analyze

Request Type: multipart form-data

### Request Data

Uploaded files

question: user-provided query

tone: response tone

### Supported Tones

executive

simple

## History Management

Every analysis request and response is stored in the backend SQLite database.

Analysis history is fetched dynamically from backend APIs.

Users can access previous analyses via:

Recent Analyses section in the sidebar

History page in the UI

Selecting a previous record reloads its results in the UI.

### Data will be stored in SQLite.
