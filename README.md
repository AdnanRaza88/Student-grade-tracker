# GradePulse - Student Grade Tracker

**Author:** Adnan Raza (ID: 0267)

## Setup
1. `python -m venv venv`
2. `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and add Groq API key
5. Run: `uvicorn app.main:app --reload`
6. Open http://localhost:8000