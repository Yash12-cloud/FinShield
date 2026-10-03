import tempfile, os
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.models.schemas import AnalyzeTextRequest, AnalyzeResponse, ExtractResponse
from backend.detection.red_flags import detect, registration_claims
from backend.detection.scoring import level, mercury_fallback_level
from backend.services.mercury import decide
from backend.services.evidence import build_evidence
from backend.services.llm import explain
from backend.services.ocr import extract_text
from backend.utils.i18n import SUPPORTED

router = APIRouter(prefix="/api/v1")

LEVEL_DISPLAY = {"low": "LOW CONCERN", "moderate": "MODERATE CONCERN", "high": "HIGH CONCERN"}


def _safe_locale(locale):
    return locale if locale in SUPPORTED else "en"


def _run_pipeline(text: str, locale: str = "en", extracted: bool = False) -> AnalyzeResponse:
    locale = _safe_locale(locale)
    categories = detect(text)
    reg_claims = registration_claims(text)
    category_level = level(categories)
    mercury = decide(text, categories, category_level)
    mercury_level = str(mercury.get("risk_level", mercury_fallback_level(category_level))).lower()
    display_level = LEVEL_DISPLAY.get(mercury_level, category_level)
    evidence = build_evidence(categories, text, reg_claims)
    llm_out = explain(text, {
        "risk_level": display_level,
        "content_type": mercury.get("content_type", "unclear"),
        "risk_categories": categories,
        "mercury": mercury,
        "evidence": evidence,
    }, locale=locale)
    assessment = {
        "steps": [
            {
                "label": "Content extraction",
                "detail": "Text extracted from screenshot (OCR) and reviewed by the user."
                if extracted else "Text received directly from the user.",
                "status": "done",
            },
            {
                "label": "Risk signals",
                "detail": ", ".join(c["label"] for c in categories) if categories else "None detected",
                "status": "done",
            },
            {
                "label": "Structured assessment",
                "detail": f"Risk level: {display_level}; Verification required: {'yes' if bool(mercury.get('requires_verification', bool(categories))) else 'no'}",
                "status": "done",
            },
            {
                "label": "Evidence",
                "detail": "Pattern-based signals separated from sources that require independent verification.",
                "status": "done",
            },
            {
                "label": "Explanation",
                "detail": "Generated from the detected signals and available evidence.",
                "status": "done",
            },
        ],
        "deterministic_categories": [c["id"] for c in categories],
        "mercury_source": mercury.get("source", "deterministic_fallback"),
        "limitation": "FinShield identifies risk indicators and verification gaps. It cannot determine with certainty whether a message is fraudulent from its content alone.",
    }
    return AnalyzeResponse(
        risk_level=display_level,
        content_type=mercury.get("content_type", "unclear"),
        severity=str(mercury.get("severity", mercury_level)),
        requires_verification=bool(mercury.get("requires_verification", bool(categories))),
        risk_categories=categories,
        mercury=mercury,
        evidence=evidence,
        explanation=llm_out.get("explanation", ""),
        verification_steps=llm_out.get("verification_steps", []),
        safe_next_steps=llm_out.get("safe_next_steps", []),
        uncertainty=llm_out.get("uncertainty", ""),
        assessment=assessment,
    )


@router.post("/analyze/text", response_model=AnalyzeResponse)
def analyze_text(req: AnalyzeTextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    return _run_pipeline(req.text, req.locale)


@router.post("/analyze/claim", response_model=AnalyzeResponse)
def analyze_claim(req: AnalyzeTextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    return _run_pipeline(req.text, req.locale)


@router.post("/extract/image", response_model=ExtractResponse)
def extract_image(file: UploadFile = File(...)):
    """OCR only. Returns extracted text for the user to review/edit before analysis."""
    suffix = os.path.splitext(file.filename or "img.png")[1]
    path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.file.read())
            path = tmp.name
        text = extract_text(path)
    except Exception:
        text = ""
    finally:
        if path and os.path.exists(path):
            os.unlink(path)
    if not text.strip():
        return ExtractResponse(
            text="",
            ok=False,
            message="We could not read text from this image. Please type or paste the message instead.",
        )
    return ExtractResponse(text=text, ok=True, message="Extracted text. Please check it before analysis.")


@router.post("/analyze/image", response_model=AnalyzeResponse)
def analyze_image(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "img.png")[1]
    path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file.file.read())
            path = tmp.name
        text = extract_text(path)
    finally:
        if path and os.path.exists(path):
            os.unlink(path)
    if not text.strip():
        raise HTTPException(status_code=422, detail="OCR could not extract text")
    return _run_pipeline(text, "en", extracted=True)