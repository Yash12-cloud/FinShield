# SANGYAN Hackathon — Project Context

## Hackathon
- Name: SANGYAN — Investor Resilience Hackathon
- Org: SNTC, IIT (BHU) Varanasi, in collaboration with SEBI & NSDL
- Duration: 4-day online, Oct 1–4, 2026
- NOTE (2026-10-02): Actual working time is ~12 hours, not the full 4 days. Prioritise a tight MVP and a demo-ready single core flow over breadth.
- Team: 1–4 members, college students, free, certificate for all
- Mode: Online; open-source tech + commercial APIs allowed (disclose third-party components)

## Mission
Build a tech product that strengthens financial resilience of Indian retail investors — first-time investors, Tier-2/3 cities, regional-language users, elderly, low digital/financial literacy. Goal: users lose less, decide rationally, understand products, recognise risk, build healthy habits.

## Tracks
- A: Digital Fraud & Scam Resilience (scam verifier, tip-group risk profiler)
- B: Investor Awareness, Rights & Grievance (SCORES assistant, nominee/wealth tracker, IEPF)
- C: Investor Education for Bharat (voice explainers, consequence simulator, regional languages)
- D: Financial Habits & Behavioural Resilience (cooling-off circuit breaker, decision journal)
- E: Misinformation & Content Literacy (claim evidence-checker, promotion vs education classifier)
- Open Track: accessibility-first tools, IVR/USSD/missed-call, AA/DigiLocker/Bhashini integration, community fraud reporting, plain-language corporate actions

## Guardrails (disqualification if violated)
- No stock tips, buy/sell/hold signals, price predictions, trading algos, broker/product promotion
- No monetisation funnels (broking commissions, upsells)
- Privacy by design: no unauthorised SMS/OTP/PII financial record harvesting
- Not investment returns advice — educational/simulation/safety use of data only
- Uncertainty must be communicated honestly; not binary true/false verdicts

## Evaluation Criteria
1. Investor Resilience & Safety
2. Bharat-First Usability & Accessibility (regional languages, low-bandwidth, voice, varying literacy)
3. Trust, Privacy & Guardrail Compliance
4. Technical Execution & Real-World Feasibility (functional prototype + deployment path)
5. Impact & Scalability

## Submission Requirements
- Working prototype (core functionality)
- Problem statement
- Solution overview
- Tech details (architecture, AI/ML, APIs, datasets)
- Demo video 3–5 min
- Impact & scalability

## Decision Log
- 2026-10-02: Build window is ~12 hours. Choose one focused MVP flow; demo > feature breadth.
- 2026-10-02: Leading idea — "Satark" (Scam & Claim Verifier, voice-first, Hindi, rule-based + optional LLM). Awaiting user confirmation before scaffolding.
- 2026-10-02: Direction chosen — **FinShield** (PRD at `FinShield_PRD.md`): Streamlit + Python, rule-based red-flag engine, Jev (TypeSafe AI SDK `@typesafe-ai/sdk`, `TYPESAFE_API_KEY`) for structured decision layer, LLM API for explanations, Tesseract OCR for screenshots. Track A primary, Track E via Claim Checker toggle. Earlier `satark/` static prototype superseded — keep as reference.
- 2026-10-02 (architecture change): Jev removed entirely → **Mercury Decide** (isolated in `backend/services/mercury.py`, env `MERCURY_API_KEY`/`MERCURY_API_URL`, deterministic local fallback). New topology: Streamlit `frontend/app.py` → HTTP → **FastAPI** `backend/main.py` → red-flag engine → Mercury → evidence → LLM explanation. Endpoints: `GET /health`, `POST /api/v1/analyze/text`, `/analyze/claim`, `/analyze/image`. Config via env `MERCURY_API_KEY`, `LLM_API_KEY`, `BACKEND_URL`; API keys never exposed to Streamlit. Deploy backend to Render (`uvicorn backend.main:app --host 0.0.0.0 --port $PORT`). Priority: /health → /analyze/text → red-flag engine → Mercury → LLM → Streamlit → Render → OCR → evidence → UI.
- 2026-10-02 (status): FinShield restructured per new PRD change request. Backend + frontend scaffolded, `/health` and `/analyze/text` verified working via curl (score 70, HIGH CONCERN, Mercury fallback structured output, evidence cards, LLM-style explanation). Tests `backend/tests/test_detection.py` pass (2). Run backend: `cd finshield && PYTHONPATH=. ../.venv/bin/uvicorn backend.main:app --port 8000`; frontend: `streamlit run frontend/app.py`. NOTE: payment-pressure regex now also matches `Rs/₹` amounts.
- 2026-10-02 (keys): OpenRouter used for BOTH Mercury and LLM via `.env` (gitignored): `MERCURY_MODEL=inception/mercury-decide:free`, `LLM_MODEL=inclusionai/ling-3.1-flash`, base `https://openrouter.ai/api/v1`. Mercury Decide is a System-One decisions model — it must use `POST /api/alpha/decisions` (NOT the chat/completions endpoint); `backend/services/mercury.py` was rewritten accordingly using `choice`/`noul` questions. LLM model `inclusionai/ling-3.1-flash` does NOT support `response_format: json_object`, so `llm.py` parses JSON out of the raw text. Full pipeline verified live: Mercury returns real structured decisions (`source: "mercury"`), LLM returns real explanations + verification/safe-next-steps + uncertainty. BACKEND KEY SECURITY: API keys passed in chat/session — treat as exposed; rotate after hackathon.
- 2026-10-02 (UX hardening): No numeric score anywhere. `/analyze/*` response is now `risk_level` (from Mercury, display LOW/MODERATE/HIGH CONCERN) + `content_type` + `severity` + `requires_verification` + grouped `risk_categories` (id, label, severity, grouped matches, dynamic explanation — guaranteed-return now quotes the matched phrase instead of "no legitimate investment can guarantee returns") + `evidence` object separating pattern-based signals (`evidence_status: Pattern-based signal — not independently verified`) from regulatory claims and registration claims (INZ placeholder pattern detected) + `grievance_note` with correct SCORES wording (grievance platform, not scam-search engine). Frontend (`frontend/src/App.tsx`) rewritten to match; urgency signals now grouped (e.g. "Act NOW", "Only 10 slots", "LIMITED TIME" → one Urgency/FOMO category). Demo message test passes: 6 categories, Mercury live, no `score` field, registration flagged as placeholder-like. Note: Streamlit UI no longer exists — frontend is React/Vite. Tests: `PYTHONPATH=finshield .venv/bin/python -m pytest finshield/backend/tests -q` → 2 passed. Also fixed: `sebi[-\s]+(approved|registered)` hyphen pattern.
- 2026-10-02 (frontend swap): Streamlit frontend removed (kept as `finshield/frontend_streamlit_backup/`). New professional React + TypeScript + Vite frontend in `finshield/frontend/` (`src/App.tsx`, `src/App.css`). Features: tabs for Message / Financial Claim / Screenshot, placeholder examples in textarea, drag-and-drop screenshot upload, no gradients, per PRD guardrails. Run: `cd finshield/frontend && npx vite --port 5173` (typecheck: `npx tsc --noEmit` passes). Backend URL via `VITE_BACKEND_URL` env, defaults to `http://localhost:8000`.


## Commit Log / Changelog
- (append notable commits/changes here so future agents can resume)

## Open Questions / TODOs
- Choose track + problem statement
- Define target user journey
- Pick tech stack
