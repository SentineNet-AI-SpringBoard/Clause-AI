## 📘 Milestone 4 – UI/UX Frontend Integration

---

## 🎯Objective

This milestone focuses on building a **user-friendly UI/UX interface** for the contract analysis system.  
A **Streamlit-based frontend** is developed to allow users to upload contracts, trigger backend analysis, and view structured reports in a clean and interactive web interface.

---

## 🧠 Key Features Implemented

### 1. Streamlit Frontend Application
- Built an interactive Streamlit web application.
- Provides clean UI for contract upload and result visualization.
- Custom styling using `styles.css`.

**Outcome:**  
User-friendly web interface for non-technical users.

---

### 2. Multi-Page Navigation
- Modular pages handled inside `app_pages/`.
- Separate views for:
  - Contract Upload
  - Analysis Dashboard
  - Report Viewer

**Outcome:**  
Smooth navigation across application pages.

---
## 🛠️ Technologies Used

- **Streamlit** – Frontend framework  
- **FastAPI** – Backend API integration  
- **Python 3.11**  
- **HTML/CSS** – Custom styling  

---

## 🚀 How to Run UI Locally

### Step 1: Navigate to UI folder
## 1) Start the Backend
```bash
cd milestone3/backend
uvicorn app:app --reload --port 8000
```
## 1) Start the UI
```bash
cd milestone4/UI/UI
pip install -r requirements.txt

# Optional: point UI to a different backend base URL
set BACKEND_URL=http://127.0.0.1:8000

streamlit run app.py
```

---
## Login & Analysis History

- User authentication and contract analysis history are securely stored in the **backend SQLite database** (not in the UI).
- After successful login, every **Ask / Launch Analysis** action is automatically saved.
- Users can reopen previous analyses using the **Recent Analyses** sidebar or the **History** page.

---

## Data Sent to Backend

- Contract files are uploaded as real files through `POST /analyze` using **multipart form-data**.
- User queries from the question input box are sent as the `question` parameter.
- UI tone selections are mapped to backend processing modes:
  - `executive` – concise professional summary
  - `simple` – easy-to-understand explanation

---



