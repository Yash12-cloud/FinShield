# FinShield

*Don't trust. Verify.* — an AI-powered investor-protection tool that helps Indian retail investors evaluate suspicious financial messages, claims, and screenshots **before** acting on them.

FinShield is **not** an investment advisor. It detects risk indicators, explains why caution is warranted, and gives safe verification steps. It never gives buy/sell/hold recommendations, price predictions, or claims content is definitively a scam.

## Architecture

```
React + Vite frontend (static)
        │ HTTP
        ▼
FastAPI backend
        ├── Python rule engine (transparent red-flag categories)
        ├── Mercury Decide (structured risk decision, System One)
        ├── Evidence service (pattern-based signals vs official sources)
        └── LLM (plain-language explanation only)
```

Responsibilities are separated: **rules = signals, Mercury Decide = decision, evidence = sources, LLM = explanation, FastAPI = orchestration & guardrails**.

## Tech stack

- Backend: FastAPI, Python 3.12, OpenCV-free OCR (Tesseract via pytesseract)
- Decision model: Inception Mercury Decide (`inception/mercury-decide:free`) via OpenRouter Decisions API
- Explanation model: `inclusionai/ling-3.1-flash` via OpenRouter chat completions
- Frontend: React 18 + TypeScript + Vite

## Live deployment

- Frontend: https://finshield-frontend.antideploy.app
- Backend: https://finshield-backend.antideploy.app (`/health` → `{"status":"ok"}`)

## Run locally

```bash
cd finshield
python3 -m venv ../.venv && source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill MERCURY_API_KEY / LLM_API_KEY (OpenRouter)
PYTHONPATH=. uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd finshield/frontend
npm install
npm run dev   # http://localhost:5173
```

## API

- `GET /health`
- `POST /api/v1/analyze/text` — `{"text": "..."}`
- `POST /api/v1/analyze/claim` — `{"text": "..."}`
- `POST /api/v1/analyze/image` — multipart file upload (PNG/JPG, OCR via Tesseract)

Response shape:

```json
{
  "risk_level": "HIGH CONCERN",
  "content_type": "scam_like",
  "severity": "high",
  "requires_verification": true,
  "risk_categories": [{"id": "...", "label": "...", "severity": "...", "matches": [...], "explanation": "..."}],
  "mercury": {...},
  "evidence": {"signals": [...], "regulatory_claims": [...], "registration_claims": [...], "suspicious_links": [...], "grievance_note": "..."},
  "explanation": "...",
  "verification_steps": [...],
  "safe_next_steps": [...],
  "uncertainty": "..."
}
```

## Tests

```bash
cd finshield
PYTHONPATH=. ../.venv/bin/python -m pytest backend/tests -q
```

## Guardrails

- No buy/sell/hold tips, no stock predictions, no broker promotion
- No numeric scam probabilities or fake confidence scores
- Wording communicates uncertainty ("risk indicators detected", not "definitely a scam")
- Privacy by design: user-provided content only; no SMS/OTP harvesting; keys live in `.env`/app secrets, never in the frontend bundle

## Repo layout

```
finshield/
├── backend/          # FastAPI app, routes, services, detection, models
├── frontend/         # React + TypeScript + Vite
├── Dockerfile        # backend deploy image
└── requirements.txt
docs/CONTEXT.md       # running project context/decision/change log
FinShield_PRD.md      # product requirements
ps.md                 # hackathon problem statement
```

Built for the SANGYAN Investor Resilience Hackathon (SEBI/NSDL/IIT-BHU).
