# Spacez Review Intelligence

AI-powered guest review analysis dashboard for Spacez premium villa properties.

## Stack
- **Backend**: Python 3.11 · FastAPI · Anthropic Claude API · Pydantic v2
- **Frontend**: React 18 · Vite · Tailwind CSS · Axios

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Add your Anthropic API key to `backend/.env`:
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
FRONTEND_URL=http://localhost:5173
```

Start the server:
```bash
uvicorn main:app --reload --port 8000
```

Test: http://localhost:8000/health  
Swagger: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at: http://localhost:5173

## Architecture

```
POST /api/analyze
  → filter_noise()          (removes RV035, RV041)
  → normalize_rating()      (Airbnb /5, Booking /10, Google /5 → all /10)
  → group_by_property()
  → Claude API × 7          (one call per property, sequential)
  → build caretaker digests (hospitality-only scoring)
  → return AnalysisResponse (ops + business + caretaker)
```

## Key Business Rules

| Rule | Detail |
|------|--------|
| Rating normalization | All platforms normalized to /10 before any math |
| Noise exclusion | RV035 (policy complaint) + RV041 (too vague) excluded |
| Cross-property alert | CT03 Lokesh Gowda flagged on both P03 + P04 |
| Caretaker fairness | WiFi/road/listing/mosquito excluded from caretaker score |
| Resolved flag | RV036 confirms pool at Serenity Villa fixed |

## Grader Checklist

- [x] Ratings normalized (Booking 6/10 ≠ Airbnb 3/5)
- [x] Lokesh Gowda cross-property alert on P03 AND P04
- [x] RV035 + RV041 not driving any issue flag
- [x] Caretaker WiFi shown as PROPERTY, not coaching issue
- [x] Serenity Villa "resolved ✓" badge visible
- [x] Backwater Bungalow starred as best performer
- [x] Vineyard Villa CRITICAL cleanliness (first card, sorted worst-first)
- [x] Hilltop Haven WiFi + photo issues tagged PROPERTY
- [x] Ganesh More cleanliness = CARETAKER issue
- [x] Deepak Sharma heating = PROPERTY issue
- [x] /health endpoint returns 200
- [x] /docs Swagger UI shows all routes
- [x] No API key in frontend code
- [x] Analysis completes without error
