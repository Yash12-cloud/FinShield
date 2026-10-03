# FinShield — Project Brief
*Don't trust. Verify.*

**Context:** SANGYAN Investor Resilience Hackathon, 1–4 October 2026 · approximately 12-hour MVP build.  
**Tracks:** A — Digital Fraud & Scam Resilience; E — Misinformation & Content Literacy.

## Problem and objective
First-time Indian investors encounter investment promotions, impersonation and unsupported financial claims through messaging apps and social media. Many lack the knowledge to verify these messages before transferring money or sharing credentials. FinShield helps them pause, recognise warning signs and decide what to verify. Primary users are inexperienced investors in Tier-2/3 cities; secondary users include elderly people and those with limited financial literacy.

## Solution and MVP scope
The core journey is **submit content → review warning signs → understand uncertainty → verify before acting**. Users paste a message or financial claim, or submit a screenshot through the OCR pathway. The report provides:
- LOW, MODERATE or HIGH CONCERN, with grouped indicators and matched phrases—not a numerical scam probability.
- Explanations of guaranteed-return language, urgency, payment pressure, credential requests and questionable authority claims.
- Clearly labelled unverified claims, official-source references and practical verification steps.

The MVP identifies patterns; it does not independently establish fraud, authenticate registrations or verify linked websites.

## Technical approach and current status
A React/TypeScript/Vite interface connects to a Python FastAPI backend. Transparent rules identify signals; Mercury Decide supplies structured assessments; a separate LLM explains the results. Model calls use OpenRouter, with deterministic fallbacks. Tesseract extracts screenshot text.

The repository contains the interface, analysis endpoints, rules, fallback logic and deployment configuration. Project notes record a verified text pipeline. Full screenshot and deployment behaviour require pre-demo validation.

## Delivery and success criteria
Within the short build window, prioritise the text flow, then validate screenshots, failure handling and deployment. The submission package comprises a functional prototype, problem and solution summary, technical details and third-party disclosures, a 3–5-minute demo video, and an impact/scalability summary.

**Acceptance targets:** complete the core demonstration in under two minutes; explain indicators and uncertainty; provide safe verification steps; evaluate at least eight representative scenarios, including benign and ambiguous content. These are targets, not reported results. Reduced susceptibility to manipulation remains an outcome to validate with users.

## Safety, dependencies and next steps
No investment tips, buy/sell/hold signals, price predictions, broker promotion, monetisation funnels or unauthorised PII/SMS/OTP collection. API keys remain server-side. Only user-submitted content enters the workflow; model-enabled scans send text to third-party services, so privacy disclosures and provider retention terms need review.

Key risks are false positives or missed warnings, model availability/latency, and OCR quality and language-pack support. Future scope includes validated regional-language interfaces, voice access and permitted registry integrations—not current MVP commitments.

**TBD:** named owner/team, budget and quantitative impact targets.

*Basis: current implementation, README.md, docs/CONTEXT.md and FinShield_PRD.md; current architecture supersedes the PRD's early technology choices.*
