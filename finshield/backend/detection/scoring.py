def level(categories) -> str:
    """Derive a display-level concern from detected categories. No numeric score."""
    if not categories:
        return "LOW CONCERN"
    if any(c.get("severity") == "high" for c in categories):
        return "HIGH CONCERN"
    return "MODERATE CONCERN"

def mercury_fallback_level(label: str) -> str:
    return {"LOW CONCERN": "low", "MODERATE CONCERN": "moderate", "HIGH CONCERN": "high"}.get(label, "unclear")
