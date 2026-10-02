# FinShield (project folder)

See the root [README](../README.md) for setup, architecture, and deployment.

Quick local run:

```bash
cd finshield
pip install -r requirements.txt
cp .env.example .env
PYTHONPATH=. uvicorn backend.main:app --port 8000
# frontend (separate terminal)
cd frontend && npm install && npm run dev
```
