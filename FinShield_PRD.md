# FinShield --- Product Requirements Document (PRD)

## 1. Product Overview

**Product name:** FinShield\
**Tagline:** *Don't trust. Verify.*\
**Hackathon:** SANGYAN --- Investor Resilience Hackathon\
**Build constraint:** 12-hour MVP\
**Primary track:** Track A --- Digital Fraud & Scam Resilience\
**Secondary track:** Track E --- Misinformation & Financial Content
Literacy

FinShield is a lightweight AI-powered financial-content safety tool that
helps an Indian investor examine a suspicious financial message,
social-media claim, promotional post, or screenshot **before acting on
it**.

The product does **not** give investment advice, stock tips,
buy/sell/hold signals, or price predictions. Instead, it identifies risk
indicators, evaluates the claim/message structure, explains why caution
may be warranted, and gives the user safe verification steps.

The hackathon brief emphasizes helping investors detect fraud, recognize
misleading information, and make safer decisions. It also specifically
calls for uncertainty to be communicated rather than reducing financial
claims to a simplistic true/false verdict.

------------------------------------------------------------------------

# 2. Problem Statement

Retail investors increasingly encounter financial information through
WhatsApp, Telegram, Instagram, YouTube, and other digital channels.

A first-time investor may receive messages containing:

-   guaranteed-return claims
-   fake or unverifiable authority claims
-   urgency and FOMO
-   requests to move to private Telegram/WhatsApp groups
-   requests for money or credentials
-   misleading statistics
-   promotional content presented as education
-   impersonation of regulators, brokers, analysts, or financial
    professionals

The user often has to decide whether to trust the message before they
have enough information to verify it.

FinShield addresses the decision point:

> **"I received this financial message. What should I check before I
> trust it or act on it?"**

------------------------------------------------------------------------

# 3. Target User

### Primary user

A first-time or inexperienced investor from a Tier-2/Tier-3 Indian city
who receives financial content through WhatsApp, Telegram, Instagram,
YouTube, or similar channels.

### Secondary users

-   Senior citizens vulnerable to impersonation
-   Users who nearly fell for a financial scam
-   Users who are more comfortable with simple language than financial
    jargon

The interface should use plain language and avoid assuming financial
knowledge.

------------------------------------------------------------------------

# 4. Product Goal

FinShield should help a user:

1.  Pause before acting.
2.  Identify suspicious patterns.
3.  Understand why those patterns matter.
4.  Separate claims from evidence.
5.  Know what needs independent verification.
6.  Avoid sharing money, OTPs, passwords, or sensitive information
    prematurely.
7.  Make the final decision themselves.

------------------------------------------------------------------------

# 5. Non-Goals / Guardrails

FinShield MUST NOT:

-   recommend buying, selling, or holding securities
-   predict stock prices
-   rank stocks or financial instruments
-   provide personalized investment recommendations
-   promote a specific broker or financial product
-   guarantee that content is a scam
-   harvest private SMS, OTPs, contacts, or financial records
-   create a monetization funnel
-   pressure the user into any financial action

The system should use language such as:

> "High-risk indicators detected"

rather than:

> "This is definitely a scam."

The system must expose uncertainty and explain the evidence behind its
assessment.

------------------------------------------------------------------------

# 6. Core Product Concept

## One input → Multiple safety checks → Explainable result

The user can paste:

-   a WhatsApp/Telegram message
-   an Instagram/YouTube caption
-   a financial claim
-   a website URL
-   extracted text from a screenshot

FinShield processes the content through:

``` text
User Input
    ↓
Text / URL Extraction
    ↓
Rule-Based Red Flag Detection
    ↓
Jev Decision Layer
    ↓
Evidence / Verification Checks
    ↓
Risk Profile
    ↓
Plain-Language Explanation
    ↓
Safe Next Steps
```

------------------------------------------------------------------------

# 7. Key Feature Set for the 12-Hour MVP

## Feature 1 --- Financial Content Scanner

Main screen:

``` text
FINSHIELD

Don't trust. Verify.

Paste a financial message, claim,
or promotional content.

[ Text input ]

[ ANALYZE ]
```

Optional input types:

-   Text
-   URL
-   Screenshot upload

For the 12-hour MVP, text + screenshot OCR should be prioritized. URL
analysis can be implemented as an optional enhancement.

------------------------------------------------------------------------

## Feature 2 --- Red Flag Detection

The system detects indicators such as:

### Guaranteed returns

Examples:

-   "guaranteed 30% return"
-   "risk-free profit"
-   "fixed monthly profit"

### Urgency / FOMO

Examples:

-   "only 10 slots left"
-   "act now"
-   "last opportunity"
-   "don't miss out"

### Authority / impersonation

Examples:

-   "SEBI approved"
-   "official government scheme"
-   regulator/broker impersonation language

### Payment pressure

Examples:

-   "send ₹10,000 now"
-   "pay registration fee"
-   "deposit before midnight"

### Credential requests

Examples:

-   OTP
-   UPI PIN
-   password
-   remote-access application

### Social-group migration

Examples:

-   "join our VIP Telegram"
-   "DM me on WhatsApp"
-   "private signals group"

### Promotional language

Examples:

-   "100% profit"
-   "secret strategy"
-   "guaranteed wealth"
-   "insider opportunity"

### Evidence weakness

Claims with no source, vague sources, unverifiable statistics, or
unsupported certainty.

------------------------------------------------------------------------

# 8. Feature 3 --- Jev Decision Layer

## Yes --- Jev is a very good fit for this part.

TypeSafe describes Jev as a System One model designed for **structured
decisions**, where software provides context and focused questions and
receives typed decisions/confidence rather than generated prose. The
official TypeScript SDK is `@typesafe-ai/sdk`, and TypeSafe's guide
documents Node.js 20+ for the SDK.

That makes Jev useful for the **decision layer**, not the explanation
layer.

### Jev should NOT be responsible for:

-   writing the final explanation
-   generating long educational text
-   calculating exact financial outcomes
-   acting as a general chatbot

### Jev SHOULD be responsible for:

-   classifying risk indicators
-   choosing a risk category
-   scoring severity
-   deciding whether evidence review is needed
-   deciding whether the case should be escalated to a deeper analysis
    step

Example conceptual questions:

``` text
risk_level:
    low
    moderate
    high

content_type:
    education
    promotion
    suspicious_promotion
    scam_like
    unclear

requires_verification:
    yes
    no

urgency_signal:
    none
    mild
    strong

credential_risk:
    none
    present
```

Jev's structured output can then be used by ordinary application code.

### Important architecture principle

**Jev decides.** **Rules provide deterministic checks.** **An LLM
explains.** **Code controls what the application does.**

This is safer and easier to demonstrate than asking one LLM to do
everything.

------------------------------------------------------------------------

# 9. Recommended AI Architecture

``` text
                    USER
                      │
                      ▼
              ┌───────────────┐
              │   Streamlit   │
              │      UI       │
              └───────┬───────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Input Processor │
             │ OCR / cleaning │
             └────────┬────────┘
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
 ┌──────────────────┐    ┌─────────────────┐
 │ Deterministic    │    │      Jev        │
 │ Red Flag Engine  │    │ Decision Layer  │
 └────────┬─────────┘    └────────┬────────┘
          │                       │
          └───────────┬───────────┘
                      ▼
             ┌─────────────────┐
             │ Evidence Layer  │
             │ URL/source check│
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Generative LLM  │
             │ Explanation     │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Safety Report   │
             └─────────────────┘
```

------------------------------------------------------------------------

# 10. Technology Stack

## Frontend

**Streamlit**

Why:

-   fastest to build in 12 hours
-   Python-native
-   easy file upload
-   easy deployment
-   ideal for a hackathon MVP

Optional later:

-   React
-   browser extension UI

------------------------------------------------------------------------

## Backend

**Python**

Recommended structure:

``` text
app/
├── ui/
├── services/
├── detection/
├── ai/
├── evidence/
└── utils/
```

For the 12-hour MVP, a separate FastAPI backend is optional.

If time is limited:

``` text
Streamlit → Python services directly
```

If the team already has time and wants a cleaner architecture:

``` text
Streamlit/React → FastAPI → AI services
```

------------------------------------------------------------------------

## Decision Model

**TypeSafe AI --- Jev**

Official SDK:

``` bash
npm install @typesafe-ai/sdk
```

Use Jev from a small Node.js/TypeScript service.

Recommended Node.js version:

``` text
Node.js 20+
```

Keep the TypeSafe API key server-side.

Environment variable:

``` text
TYPESAFE_API_KEY=...
```

Jev output is used for structured classification/scoring rather than
natural-language generation.

------------------------------------------------------------------------

## Generative Model

Use one existing LLM API for explanation generation.

Examples:

-   OpenAI API
-   Gemini API
-   Anthropic API
-   another hackathon-provided model

The LLM receives the structured analysis and generates:

-   plain-language explanation
-   evidence summary
-   verification checklist
-   safe next steps

The LLM should NOT be allowed to override deterministic safety rules.

------------------------------------------------------------------------

## OCR

For screenshot input:

**Tesseract OCR**

or a cloud vision/OCR API if already available.

12-hour priority:

``` text
Screenshot
   ↓
OCR
   ↓
Extracted text
   ↓
Normal pipeline
```

------------------------------------------------------------------------

## Rule Engine

Python:

-   regular expressions
-   keyword/pattern matching
-   URL parsing
-   deterministic scoring

Example:

``` python
RED_FLAGS = {
    "guaranteed_return": [...],
    "urgency": [...],
    "credential_request": [...],
    "payment_pressure": [...],
    "social_group": [...],
    "authority_claim": [...],
}
```

Rules provide transparent evidence:

``` text
Matched phrase:
"guaranteed 30% monthly returns"

Rule:
GUARANTEED_RETURN

Reason:
Promises of guaranteed financial returns require
independent verification.
```

------------------------------------------------------------------------

## Evidence Layer

For the MVP, the evidence layer should:

1.  Extract claims.
2.  Identify claims requiring verification.
3.  Check supplied URLs/domains where practical.
4.  Provide links to official sources where applicable.
5.  Clearly label unverified claims.

Do not claim that a source is official unless it has been verified.

For the demo, maintain a small curated set of official/public reference
URLs rather than trying to build a complete financial registry.

------------------------------------------------------------------------

## Database

For the MVP:

**SQLite**

Store only:

-   anonymous scan ID
-   timestamp
-   detected categories
-   risk indicators
-   optional user feedback

Do NOT store:

-   OTPs
-   bank details
-   passwords
-   private financial records
-   unnecessary personal information

An even simpler MVP can avoid persistent storage completely.

------------------------------------------------------------------------

# 11. Risk Assessment Design

Do not make the system output a fake precise probability such as:

> "87.43% scam."

Instead use understandable categories:

``` text
LOW CONCERN
MODERATE CONCERN
HIGH CONCERN
```

And show the supporting indicators.

Example:

``` text
HIGH CONCERN

5 risk indicators detected

🔴 Guaranteed-return language
🔴 Urgency / FOMO
🔴 Payment request
🟡 Authority claim needs verification
🟡 Telegram migration
```

The exact final category should be produced from the combination of
deterministic signals and Jev's structured assessment.

------------------------------------------------------------------------

# 12. Example User Journey

## Scenario

A first-time investor receives:

``` text
SEBI APPROVED INVESTMENT 🚨

Earn 30% guaranteed every month.

Only 10 slots remaining!

Send ₹10,000 to activate your account.

Join our VIP Telegram group:
t.me/example
```

### Step 1

User pastes the message.

### Step 2

FinShield extracts the text.

### Step 3

Rule engine identifies:

``` text
guaranteed return
urgency
payment request
Telegram migration
authority claim
```

### Step 4

Jev evaluates structured questions about:

-   content type
-   severity
-   urgency
-   credential/payment risk
-   need for verification

### Step 5

Evidence layer marks the authority claim for independent verification.

### Step 6

LLM generates a plain-language explanation.

### Step 7

UI displays:

``` text
HIGH CONCERN

Why?

• The message promises a guaranteed return.
• It uses urgency to pressure immediate action.
• It asks the user to transfer money.
• It claims regulatory approval that should be
  independently verified.
• It moves the conversation to a private Telegram group.

Before acting:

✓ Verify the entity through an official source.
✓ Do not share OTPs, passwords or UPI PINs.
✓ Do not transfer money based only on this message.
✓ Look for independent evidence for the claims.

This analysis identifies risk indicators.
It is not a legal determination that the message is fraudulent.
```

------------------------------------------------------------------------

# 13. Second Demo Mode --- Claim Checker

Add a toggle:

``` text
[ SCAM / MESSAGE SCAN ] [ CLAIM CHECK ]
```

Claim example:

> "This investment is guaranteed to double your money in 3 years."

Output:

``` text
CLAIM REQUIRES VERIFICATION

Claim:
"Guaranteed to double your money in 3 years."

Problems detected:

🟡 Guaranteed outcome
🟡 No supporting source
🟡 Missing assumptions

What is missing?

• Expected return assumption
• Fees
• Risk
• Investment conditions
• Evidence/source

Conclusion:

Do not treat this statement as established fact
without checking the underlying evidence.
```

This gives you both Track A and Track E coverage without building two
separate products.

------------------------------------------------------------------------

# 14. UI Design

## Home

Minimal, mobile-friendly layout.

``` text
━━━━━━━━━━━━━━━━━━━━━━━━━━
        FINSHIELD
      Don't trust. Verify.
━━━━━━━━━━━━━━━━━━━━━━━━━━

What did you receive?

○ Message
○ Financial Claim
○ Screenshot

┌─────────────────────────┐
│ Paste content here...   │
│                         │
└─────────────────────────┘

        [ ANALYZE ]

Your data is not used for
investment recommendations.
```

------------------------------------------------------------------------

## Results

``` text
━━━━━━━━━━━━━━━━━━━━━━━━━━
       HIGH CONCERN
━━━━━━━━━━━━━━━━━━━━━━━━━━

5 risk indicators detected

🔴 Guaranteed returns
🔴 Urgency
🔴 Payment request
🟡 Authority claim
🟡 Private Telegram group

──────────────────────────

WHY THIS MATTERS

[Plain-language explanation]

──────────────────────────

VERIFY BEFORE ACTING

1. Verify the claimed entity.
2. Check the original source.
3. Don't share credentials.
4. Don't transfer money yet.

──────────────────────────

[ VIEW EVIDENCE ]
[ ANALYZE ANOTHER ]
```

------------------------------------------------------------------------

# 15. Language Support

For the hackathon MVP:

### English

Full support.

### Hindi

Basic UI + generated explanations.

### Marathi

Basic UI + generated explanations if the selected LLM supports reliable
Marathi output.

The system should keep financial terminology simple and explain jargon
using everyday language.

Example:

``` text
Volatility

Simple meaning:
How much the value of an investment can move
up and down over time.
```

------------------------------------------------------------------------

# 16. Privacy

Privacy is a core requirement.

### Do

-   process only user-provided content
-   minimize stored data
-   use environment variables for API keys
-   delete temporary uploaded screenshots after processing
-   clearly tell users what is processed

### Don't

-   read SMS automatically
-   read WhatsApp automatically
-   access OTPs
-   access banking apps
-   scrape contacts
-   collect unnecessary personal financial information

The hackathon explicitly requires privacy by design.

------------------------------------------------------------------------

# 17. API / Service Boundaries

If using the full architecture:

``` text
Frontend
    ↓
FastAPI
    ├── /analyze/text
    ├── /analyze/image
    ├── /analyze/claim
    └── /health

FastAPI
    ├── Rule Engine
    ├── Jev Service
    ├── Evidence Service
    └── LLM Explanation Service
```

However, for a 12-hour build, the recommended implementation is:

``` text
Streamlit
   ↓
Python service layer
   ↓
Jev / LLM APIs
```

Add FastAPI only if the core product is already working.

------------------------------------------------------------------------

# 18. Suggested Repository Structure

``` text
finshield/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── services/
│   ├── analyzer.py
│   ├── jev_service.py
│   ├── llm_service.py
│   └── evidence_service.py
│
├── detection/
│   ├── red_flags.py
│   ├── patterns.py
│   └── scoring.py
│
├── extraction/
│   └── ocr.py
│
├── prompts/
│   └── explanation_prompt.txt
│
├── data/
│   └── official_sources.json
│
└── tests/
    └── test_detection.py
```

------------------------------------------------------------------------

# 19. 12-Hour Build Plan

## Hour 0--1 --- Setup

-   Create repository
-   Streamlit setup
-   Environment variables
-   Basic UI
-   API keys

Deliverable:

``` text
Working homepage
```

------------------------------------------------------------------------

## Hour 1--3 --- Rule Engine

Implement:

-   guaranteed-return detection
-   urgency detection
-   payment detection
-   credential detection
-   Telegram/WhatsApp migration
-   authority claims
-   promotional language

Deliverable:

``` text
Input → detected red flags
```

------------------------------------------------------------------------

## Hour 3--5 --- Jev Integration

Implement Jev service.

Jev evaluates:

``` text
content_type
risk_level
severity
requires_verification
```

Deliverable:

``` text
Input → structured Jev decision
```

------------------------------------------------------------------------

## Hour 5--6 --- LLM Explanation

Create a strict prompt that receives:

``` text
user_text
rule_results
jev_results
evidence_results
```

and returns:

``` text
summary
why_it_matters
verification_steps
safe_next_steps
uncertainty
```

Deliverable:

``` text
Structured analysis → human-friendly explanation
```

------------------------------------------------------------------------

## Hour 6--7 --- Screenshot OCR

Add:

``` text
Upload screenshot
      ↓
OCR
      ↓
Extracted text
      ↓
Existing analyzer
```

If OCR becomes unstable, skip it and perfect text analysis.

------------------------------------------------------------------------

## Hour 7--8 --- Evidence Layer

Add:

-   official-source references
-   URL extraction
-   source verification status
-   evidence cards

Keep this small.

------------------------------------------------------------------------

## Hour 8--9 --- UI Polish

Focus on:

-   mobile-friendly layout
-   clear risk indicators
-   readable typography
-   simple language
-   demo examples
-   Hindi/Marathi toggle if time permits

------------------------------------------------------------------------

## Hour 9--10 --- Testing

Prepare at least 8 test cases:

1.  Obvious scam
2.  Investment promotion
3.  Legitimate educational content
4.  Ambiguous claim
5.  Guaranteed return claim
6.  Fake authority claim
7.  Credential request
8.  Normal financial education

Check false positives.

------------------------------------------------------------------------

## Hour 10--11 --- Deployment

Deploy Streamlit application.

Test:

-   cold start
-   API failures
-   empty input
-   invalid screenshot
-   missing API key
-   slow model response

Add fallback behavior.

------------------------------------------------------------------------

## Hour 11--12 --- Submission

Prepare:

### 3--5 minute video

``` text
0:00 Problem
0:30 User receives suspicious message
1:00 Paste into FinShield
1:30 Rule + Jev analysis
2:00 Evidence
2:30 Explanation
3:00 Safe next steps
3:30 Why it matters
4:00 Future scope
```

### PPT

1.  Problem
2.  Target user
3.  Existing gap
4.  FinShield
5.  User journey
6.  Architecture
7.  Jev + AI architecture
8.  Privacy/guardrails
9.  Demo
10. Future scope

------------------------------------------------------------------------

# 20. MVP Acceptance Criteria

The MVP is successful if:

-   [ ] User can paste a financial message.
-   [ ] User can submit a financial claim.
-   [ ] System detects multiple red-flag categories.
-   [ ] Jev produces structured decisions.
-   [ ] System does not provide investment recommendations.
-   [ ] System explains detected indicators.
-   [ ] System communicates uncertainty.
-   [ ] System provides verification steps.
-   [ ] Screenshot OCR works OR is cleanly omitted if unstable.
-   [ ] API keys are not exposed in frontend code.
-   [ ] No private SMS/OTP/banking data is collected.
-   [ ] Demo can be completed end-to-end in under 2 minutes.

------------------------------------------------------------------------

# 21. Future Scope

After the hackathon:

### Browser Extension

User right-clicks financial content:

``` text
Check with FinShield
```

### WhatsApp Share Sheet

Share suspicious text to FinShield.

### Voice Mode

User speaks:

> "Someone sent me this investment offer. Is there anything suspicious?"

FinShield responds in Hindi/Marathi/English.

### Regional Languages

Expand to:

-   Hindi
-   Marathi
-   Bengali
-   Tamil
-   Telugu
-   Kannada
-   Gujarati

### Community Reporting

Allow anonymized reporting of scam patterns.

### Official Registry Integrations

Integrate with relevant public regulatory/financial registries where
permitted.

------------------------------------------------------------------------

# 22. Key Product Principle

FinShield should never tell the user:

> "Invest."

It should help the user ask:

> "What should I verify before I act?"

That distinction is central to the hackathon's investor-resilience
objective.

------------------------------------------------------------------------

# 23. One-Line Pitch

> **FinShield is an AI-powered financial safety layer that helps Indian
> investors detect manipulation, evaluate financial claims, and know
> what to verify before money changes hands.**

------------------------------------------------------------------------

# 24. Technical Pitch

> **FinShield combines deterministic red-flag detection, TypeSafe AI's
> Jev decision model for fast structured risk judgments, evidence
> checks, and a generative LLM for plain-language explanations ---
> creating an explainable, uncertainty-aware investor-protection
> workflow rather than an investment advisor.**

------------------------------------------------------------------------

# 25. Why Jev Fits FinShield

Jev is particularly suitable for the parts of FinShield that require
bounded decisions:

``` text
MESSY FINANCIAL CONTENT
        ↓
       JEV
        ↓
┌─────────────────────────┐
│ Content type            │
│ Risk category           │
│ Severity                │
│ Verification required   │
│ Urgency signal          │
│ Credential risk         │
└─────────────────────────┘
        ↓
ORDINARY APPLICATION CODE
        ↓
LLM EXPLANATION
```

This separation gives the system a clean architecture:

**Jev = decision**

**Rules = transparent signals**

**LLM = explanation**

**Code = enforcement**

------------------------------------------------------------------------

# 26. References

Primary hackathon source:

-   SANGYAN Investor Resilience Hackathon --- Problem Statement &
    Participant Charter, supplied in this project.

Jev / TypeSafe AI:

-   TypeSafe AI --- What is Jev?
-   TypeSafe AI --- Use Jev from TypeScript
-   TypeSafe AI --- Introducing System One Models & Jev

The Jev integration details in this PRD should be checked against the
current TypeSafe AI documentation before deployment because Jev is a
newly released service and its SDK/API details may change.
