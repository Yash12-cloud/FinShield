import re

CATEGORY_META = {
    "guaranteed_return": {"label": "Guaranteed Return", "severity": "high"},
    "urgency_fomo": {"label": "Urgency / FOMO", "severity": "high"},
    "authority_impersonation": {"label": "Regulatory Claim", "severity": "moderate"},
    "payment_pressure": {"label": "Payment Request", "severity": "high"},
    "credential_request": {"label": "Credential Request", "severity": "high"},
    "social_group_migration": {"label": "Private Group Migration", "severity": "moderate"},
    "promotional_language": {"label": "Promotional Language", "severity": "moderate"},
    "evidence_weakness": {"label": "Weak Evidence", "severity": "moderate"},
}

PATTERNS = {
    "guaranteed_return": [
        r"guarantee\w*\s+\d+%", r"risk[-\s]?free\s+(profit|return)", r"fixed\s+monthly\s+profit",
        r"\d+%\s+(guaranteed|fixed|assured)", r"100%\s+profit", r"double\s+your\s+money",
        r"zero\s+risk", r"निश्चित\s*(लाभ|रिटर्न)", r"गारंटी",
    ],
    "urgency_fomo": [
        r"act\s+now", r"only\s+\d+\s+slots", r"last\s+(opportunity|chance)", r"don'?t\s+miss\s+out",
        r"limited\s+time", r"everyone\s+is\s+already\s+joining", r"आज\s+ही", r"जल्दी", r"अभी\s+जुड़",
    ],
    "authority_impersonation": [
        r"sebi[-\s]+(approved|registered)", r"official\s+government\s+scheme", r"government\s+backed",
        r"rbi\s+approved", r"SEBI\s*पंजीकृत",
    ],
    "payment_pressure": [
        r"send\s+₹\s*[\d,]+", r"pay\s+registration\s+fee", r"deposit\s+before", r"pay\s+now",
        r"send\s+rs\.?\s*[\d,]+", r"pay\s+rs\.?\s*[\d,]+", r"minimum\s+investment",
        r"ट्रांसफर\s+करें", r"भुगतान\s+करें",
    ],
    "credential_request": [
        r"\botp\b", r"upi\s+pin", r"password", r"remote[-\s]?access", r"anydesk", r"teamviewer",
        r"ओटीपी", r"remote",
    ],
    "social_group_migration": [
        r"join\s+our\s+vip\s+telegram", r"t\.me/", r"dm\s+me\s+on\s+whatsapp", r"private\s+signals\s+group",
        r"whatsapp\s+group", r"vip\s+group", r"vip\s+telegram", r"टेलीग्राम",
    ],
    "promotional_language": [
        r"secret\s+strategy", r"guaranteed\s+wealth", r"insider\s+opportunity", r"multibagger",
        r"free\s+calls", r"free\s+tips", r"secret\s+tip", r"guaranteed\s+profit\s+signals",
    ],
    "evidence_weakness": [
        r"trust\s+me", r"believe\s+me", r"everyone\s+is\s+earning", r"no\s+proof\s+needed",
        r"हर\s+कोई\s+कमा\s+रहा",
    ],
}

def _explanation(category: str, matches: list) -> str:
    first = matches[0] if matches else "this claim"
    if category == "guaranteed_return":
        return f'A claim of "{first}" is an extraordinary claim that requires strong independent verification.'
    if category == "urgency_fomo":
        return "These phrases create pressure to act quickly and discourage independent checking."
    if category == "authority_impersonation":
        return (
            f"The message claims to be '{first}'. This should be independently verified. "
            "A registration claim in a message does not by itself establish that the specific offer is legitimate."
        )
    if category == "payment_pressure":
        return "Avoid transferring money until the offer and the entity have been independently verified."
    if category == "credential_request":
        return "Never share OTPs, passwords, UPI PINs, or remote-access permissions with anyone."
    if category == "social_group_migration":
        return "Moving communication to a private group can make independent verification more difficult."
    if category == "promotional_language":
        return "Promotional language presented as opportunity is a caution signal — check the underlying evidence yourself."
    if category == "evidence_weakness":
        return "Claims without a source or with vague evidence need independent verification."
    return "This warrants independent verification."

def find_red_flags(text: str):
    grouped = []
    for category, patterns in PATTERNS.items():
        matches = []
        for pat in patterns:
            for match in re.finditer(pat, text, re.IGNORECASE):
                m = match.group(0).strip()
                if m and m not in matches:
                    matches.append(m)
        if matches:
            meta = CATEGORY_META[category]
            grouped.append({
                "id": category,
                "label": meta["label"],
                "severity": meta["severity"],
                "matches": matches,
                "explanation": _explanation(category, matches),
            })
    return grouped

REG_NUMBER_RE = re.compile(r"\b(INZ[0-9A-Za-z]{3,}|[A-Z]{2,4}\d{4,}[A-Z0-9]?)\b")

def extract_registration_claims(text: str):
    claims = []
    for m in REG_NUMBER_RE.finditer(text):
        value = m.group(0)
        if value.upper() in ("INZ000XXXXX",) or "X" in value.upper():
            reason = "The registration number appears incomplete or placeholder-like and should be independently verified."
        else:
            reason = "The registration number as stated in the message should be independently verified against official records."
        claims.append({
            "value": value,
            "status": "Requires independent verification",
            "reason": reason,
            "official_source": "https://www.sebi.gov.in — verify registered intermediaries",
        })
    return claims
