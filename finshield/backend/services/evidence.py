import json, os, re

_SOURCES = None

def _load():
    global _SOURCES
    if _SOURCES is None:
        path = os.path.join(os.path.dirname(__file__), "..", "data", "official_sources.json")
        with open(path, encoding="utf-8") as f:
            _SOURCES = json.load(f)
    return _SOURCES

SCORES_NOTE = (
    "SCORES is an official SEBI grievance platform. If you have experienced a grievance "
    "involving a SEBI-regulated entity, you can use SCORES to submit and track a complaint. "
    "It is not a public scam-search engine."
)

def build_evidence(categories, text: str, registration_claims: list):
    """Separates pattern-based signals from independently verifiable official sources."""
    sources = _load()
    signals = []
    for cat in categories:
        signals.append({
            "id": cat["id"],
            "label": cat["label"],
            "matches": cat["matches"],
            "assessment": "Caution signal",
            "explanation": cat["explanation"],
            "evidence_status": "Pattern-based signal — not independently verified.",
        })
    regulatory = []
    if any(c["id"] == "authority_impersonation" for c in categories) or registration_claims:
        regulatory.append({
            "claim": "Regulatory / SEBI approval claim",
            "status": "Requires independent verification",
            "official_source": sources["sebi"],
            "explanation": "A claim of SEBI registration or approval should be checked against official SEBI records. Do not assume it is valid based on the message alone.",
        })
    links = re.findall(r"https?://[^\s]+|t\.me/[^\s]+|bit\.ly/[^\s]+", text)
    link_items = [{"url": u, "status": "Unverified link — do not click blindly"} for u in links]
    return {
        "signals": signals,
        "verified_information": [],
        "regulatory_claims": regulatory,
        "registration_claims": registration_claims,
        "suspicious_links": link_items,
        "grievance_note": SCORES_NOTE,
        "sources": sources,
    }
