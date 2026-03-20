# 🏛️ CivicBridge AI

> Convert messy citizen complaints into structured government dispatch tickets using Gemini 1.5 Flash.

---

## Quick Start

### 1. Add Your Gemini API Key

Open `backend/.env` and replace the placeholder:
```
GEMINI_API_KEY=your_actual_key_here
```
Get a key at: https://aistudio.google.com/apikey

---

### 2. Install Python Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

---

### 3. Start the Backend Server

```powershell
cd backend
uvicorn main:app --reload
```

The API will be live at: **http://localhost:8000**

Check it: http://localhost:8000/api/health  
Browse API docs: http://localhost:8000/docs

---

### 4. Open the Frontend

Simply open `frontend/index.html` in your browser (Chrome recommended).

> The frontend talks to `http://localhost:8000` by default. You can change this in the **API** field at the top of the input panel.

---

## App Workflow

```
Citizen Input (text + optional photo)
        ↓
FastAPI /api/submit-complaint
        ↓
Gemini 1.5 Flash (multimodal analysis)
        ↓
Structured JSON Dispatch Ticket
        ↓
Frontend renders Ticket + Live Dashboard
```

---

## Project Structure

```
Societal Benefit/
├── backend/
│   ├── main.py           # FastAPI server
│   ├── gemini_bridge.py  # Gemini API integration
│   ├── models.py         # Pydantic schemas
│   ├── requirements.txt
│   └── .env              # ← Your API key goes here
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
└── .env.example
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Server health check |
| POST | `/api/submit-complaint` | Submit complaint (text + image) |
| GET | `/api/departments` | List all routable departments |

### POST `/api/submit-complaint` — Form Fields

| Field | Required | Description |
|-------|----------|-------------|
| `description` | ✅ | Complaint text (any language/style) |
| `location` | ⬜ | Location hint text |
| `image` | ⬜ | Photo file (JPG/PNG/WEBP, max 10 MB) |

---

## ☁️ Google Cloud Run Deployment

To deploy CivicBridge AI to the cloud:

### 1. Build and Tag
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/civicbridge-ai
```

### 2. Deploy
```bash
gcloud run deploy civicbridge-ai \
  --image gcr.io/YOUR_PROJECT_ID/civicbridge-ai \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="GEMINI_API_KEY=YOUR_KEY"
```

> [!NOTE]
> The app listens on the `$PORT` environment variable (default 8080).
