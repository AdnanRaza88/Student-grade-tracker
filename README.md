# GradePulse - Student Grade Tracker

**Developer:** AdnanRaza (ID: 0267)

## Problem Statement
Teachers need a digital system to track student grades, analyze performance, and get AI-powered study tips.

## Tech Stack
- FastAPI
- SQLModel + SQLite
- NiceGUI (frontend)
- Groq (LLM)
- Pandas (file processing)

## Setup Instructions
1. Clone repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
4. Install: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and add your Groq API key
6. Run: `uvicorn app.main:app --reload`
7. Open browser: `http://localhost:8000`

## API Endpoints
- POST /grades/
- GET /grades/
- GET /grades/{id}
- PUT /grades/{id}
- DELETE /grades/{id}
- POST /grades/{id}/study-tips
- GET /grades/stats/summary
- POST /upload/preview, /upload/validate, /upload/insert
- GET /export/csv, /export/excel

## Sample JSON
```json
{
  "student_name": "Ali",
  "father_name": "Ahmed",
  "subject": "Mathematics",
  "marks_obtained": 85,
  "total_marks": 100,
  "exam_type": "Combined",
  "semester": "Spring 2025",
  "date": "2025-01-15"
}
```

Screenshots

(Add screenshots of /docs and dashboard here)
