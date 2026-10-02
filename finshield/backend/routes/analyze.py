import tempfile, os
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.models.schemas import AnalyzeTextRequest, AnalyzeResponse
from backend.detection.red_flags import detect, registration_claims
from backend.detection.scoring import level, mercury_fallback_level
from backend.services.mercury import decide
from backend.services.evidence import build_evidence
from backend.services.llm import explain
from backend.services.ocr import extract_text

router = APIRouter(prefix="/api/v1")

LEVEL_DISPLAY = {"low": "LOW CONCERN", "moderate": "MODERATE CONCERN", "high": "HIGH CONCERN"}
SEVERITY_DISPLAY = {"low": "low", "moderate": "moderate", "high": "high"}

def _run_pipeline(text: str) -> AnalyzeResponse:
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
    })
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
    )

@router.post("/analyze/text", response_model=AnalyzeResponse)
def analyze_text(req: AnalyzeTextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    return _run_pipeline(req.text)

@router.post("/analyze/claim", response_model=AnalyzeResponse)
def analyze_claim(req: AnalyzeTextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    return _run_pipeline(req.text)

@router.post("/analyze/image", response_model=AnalyzeResponse)
def analyze_image(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "img.png")[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file.file.read())
        path = tmp.name
    try:
        text = extract_text(path)
    finally:
        os.unlink(path)
    if not text.strip():
        raise HTTPException(status_code=422, detail="OCR could not extract text")
    return _run_pipeline(text)
