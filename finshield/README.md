# FinShield

*Don't trust. Verify.* — AI-powered financial-content safety layer.

## Architecture

Streamlit frontend → HTTP → FastAPI backend → red-flag engine → Mercury Decide → evidence → LLM explanation → structured report.

## Run locally

```bash
cd finshield
python3 -m venv ../.venv && source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill keys
uvicorn backend.main:app --host 0.0.0.0 --port 8000
streamlit run frontend/app.py
```

## Endpoints

- `GET /health`
- `POST /api/v1/analyze/text` — `{"text": "..."}`
- `POST /api/v1/analyze/claim` — `{"text": "..."}`
- `POST /api/v1/analyze/image` — multipart file upload

## Deploy

Render Web Service: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`. Set `BACKEND_URL` in the Streamlit environment.

## Guardrails

No investment advice, tips, price predictions, or broker promotion. Never claims content is "definitely a scam" — it reports risk indicators and uncertainty.
