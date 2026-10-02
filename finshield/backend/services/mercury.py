import requests
from backend.utils.config import MERCURY_API_KEY, MERCURY_BASE_URL, MERCURY_MODEL

DECISIONS_URL = MERCURY_BASE_URL.replace("/v1", "") + "/alpha/decisions"

def decide(text: str, flags: list, risk_level: str) -> dict:
    """Mercury Decide (System One) produces structured decisions.
    Isolated here so the provider can be swapped without touching other code.
    Falls back to a deterministic decision when MERCURY_API_KEY is unset."""
    if MERCURY_API_KEY:
        try:
            payload = {
                "model": MERCURY_MODEL,
                "state": {"document": text, "detected_flags": [f["id"] for f in flags]},
                "questions": {
                    "risk_level": {"type": "choice", "instructions": "How risky is this content for a retail investor?", "criteria": {"low": "Informational, no strong warning signs.", "moderate": "Some caution signals present.", "high": "Multiple strong warning signs of manipulation."}},
                    "content_type": {"type": "choice", "instructions": "What type of content is this?", "criteria": {"education": "Explains concepts neutrally.", "promotion": "Promotes a product or service.", "suspicious_promotion": "Promotion with pressure or doubtful claims.", "scam_like": "Shows scam patterns like guaranteed returns or credential requests.", "unclear": "Cannot be determined."}},
                    "severity": {"type": "choice", "instructions": "Overall severity for the user.", "criteria": {"low": "Minor concern.", "moderate": "Meaningful concern.", "high": "Serious concern, likely harmful."}},
                    "requires_verification": {"type": "noul", "instructions": "Should the user independently verify this content before acting?", "criteria": {"true": "Needs independent verification.", "false": "No special verification needed."}},
                    "urgency_signal": {"type": "choice", "instructions": "How much urgency or pressure does the content apply?", "criteria": {"none": "No time pressure.", "mild": "Light suggestion to act soon.", "strong": "Strong pressure, deadlines, FOMO."}},
                    "payment_risk": {"type": "noul", "instructions": "Does the content request or pressure a payment/transfer?", "criteria": {"true": "Payment is requested or demanded.", "false": "No payment requested."}},
                    "credential_risk": {"type": "noul", "instructions": "Does the content ask for OTP, password, UPI PIN, or remote access?", "criteria": {"true": "Credentials or access are requested.", "false": "No credential request."}},
                },
            }
            resp = requests.post(DECISIONS_URL, headers={"Authorization": f"Bearer {MERCURY_API_KEY}"}, json=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            answers = data.get("answers", {})
            out = {}
            for key, ans in answers.items():
                if "choice" in ans:
                    out[key] = ans["choice"]
                elif "noul" in ans:
                    out[key] = bool(ans["noul"] > 0.5)
                elif "score" in ans:
                    out[key] = ans["score"]
            out["source"] = "mercury"
            return out
        except Exception:
            pass
    return _fallback(flags, risk_level)

def _fallback(flags: list, risk_level: str) -> dict:
    categories = {f["id"] for f in flags}
    return {
        "risk_level": "high" if risk_level == "HIGH CONCERN" else ("moderate" if risk_level == "MODERATE CONCERN" else "low"),
        "content_type": "scam_like" if {"payment_pressure", "credential_request"} & categories else (
            "suspicious_promotion" if categories else "education"
        ),
        "severity": "high" if risk_level == "HIGH CONCERN" else ("moderate" if risk_level == "MODERATE CONCERN" else "low"),
        "requires_verification": bool(flags),
        "urgency_signal": "strong" if "urgency_fomo" in categories else "none",
        "payment_risk": "payment_pressure" in categories,
        "credential_risk": "credential_request" in categories,
        "source": "deterministic_fallback",
    }
