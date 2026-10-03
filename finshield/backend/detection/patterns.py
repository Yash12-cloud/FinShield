import re

CATEGORY_META = {
    "guaranteed_return": {"label": "Guaranteed Return", "severity": "high"},
    "urgency_fomo": {"label": "Urgency / FOMO", "severity": "high"},
    "payment_pressure": {"label": "Payment Request", "severity": "high"},
    "credential_request": {"label": "Credential Request", "severity": "high"},
    "authority_impersonation": {"label": "Regulatory Claim", "severity": "moderate"},
    "social_group_migration": {"label": "Private Group Migration", "severity": "moderate"},
    "promotional_language": {"label": "Promotional Language", "severity": "moderate"},
    "evidence_weakness": {"label": "Weak Evidence", "severity": "moderate"},
    "impersonation": {"label": "Impersonation / Account Threat", "severity": "high"},
    "suspicious_link": {"label": "Suspicious Link", "severity": "moderate"},
    "social_proof": {"label": "Social Proof Pressure", "severity": "moderate"},
}

PATTERNS = {
    "guaranteed_return": [
        r"guarantee\w*\s+\d+%", r"guaranteed\s+(return|returns|profit|profit\s+signals|wealth)",
        r"risk[-\s]?free\s+(profit|return|returns)", r"fixed\s+monthly\s+(profit|return|returns)",
        r"\d+%\s+(guaranteed|fixed|assured)", r"assured\s+returns?", r"100%\s+profit",
        r"double\s+your\s+money", r"zero\s+risk", r"निश्चित\s*(लाभ|रिटर्न)", r"गारंटी",
    ],
    "urgency_fomo": [
        r"act\s+now", r"only\s+\d+\s+slots?", r"last\s+(opportunity|chance)", r"don'?t\s+miss\s+out",
        r"limited\s+time", r"offer\s+expires?", r"expires?\s+in\s+\d+", r"before\s+registration\s+closes",
        r"registration\s+closes", r"hurry", r"everyone\s+is\s+already\s+joining",
        r"आज\s+ही", r"जल्दी", r"अभी\s+जुड़",
    ],
    "payment_pressure": [
        r"send\s+₹\s*[\d,]+", r"send\s+(the\s+)?(amount|money|funds)", r"transfer\s+(the\s+)?(amount|money|funds)",
        r"pay\s+registration\s+fee", r"pay\s+to\s+activate", r"deposit\s+before", r"deposit\s+(₹|rs)",
        r"pay\s+now", r"send\s+rs\.?\s*[\d,]+", r"pay\s+rs\.?\s*[\d,]+", r"minimum\s+investment",
        r"invest\s+₹\s*[\d,]+", r"ट्रांसफर\s+करें", r"भुगतान\s+करें",
    ],
    "credential_request": [
        r"\botp\b", r"upi\s+pin", r"\bpin\b", r"password", r"verification\s+code", r"\bcvv\b",
        r"remote[-\s]?access", r"anydesk", r"teamviewer", r"ओटीपी",
    ],
    "authority_impersonation": [
        r"sebi[-\s]+(approved|registered)", r"official\s+government\s+scheme", r"government\s+backed",
        r"rbi[-\s]+approved", r"government[-\s]+approved", r"SEBI\s*पंजीकृत",
    ],
    "social_group_migration": [
        r"join\s+our\s+vip\s+telegram", r"t\.me/", r"dm\s+me\s+on\s+whatsapp", r"private\s+signals\s+group",
        r"exclusive\s+signals\s+group", r"whatsapp\s+group", r"vip\s+group", r"vip\s+telegram", r"टेलीग्राम",
    ],
    "promotional_language": [
        r"secret\s+strategy", r"guaranteed\s+wealth", r"insider\s+opportunity", r"multibagger",
        r"free\s+calls", r"free\s+tips", r"secret\s+tip", r"daily\s+guaranteed\s+profit",
    ],
    "evidence_weakness": [
        r"trust\s+me", r"believe\s+me", r"everyone\s+is\s+earning", r"no\s+proof\s+needed",
        r"हर\s+कोई\s+कमा\s+रहा",
    ],
    "impersonation": [
        r"account\s+(will\s+be\s+|is\s+)?(suspended|blocked|frozen|closed)",
        r"(suspend|block|freeze)\w*\s+your\s+(account|demat)", r"urgent\s+kyc",
        r"kyc\s+(update|verification|expiry|expires?)", r"regulatory\s+warning",
        r"update\s+your\s+(pan|kyc|details)", r"re[-\s]?kyc",
    ],
    "suspicious_link": [
        r"http://", r"\.xyz\b", r"\.top\b", r"\.click\b", r"\.work\b", r"\.online\b",
        r"bit\.ly/", r"tinyurl\.com/", r"click\s+(here|the\s+link)", r"verify\s+your\s+account\s+here",
    ],
    "social_proof": [
        r"thousands\s+(already\s+)?(invested|joined)", r"lakhs\s+of\s+(investors|people)",
        r"crores\s+of\s+(investors|people)", r"success\s+stories", r"guaranteed\s+success",
        r"everyone\s+is\s+joining",
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
    if category == "impersonation":
        return "Threats about account suspension or urgent KYC are a common impersonation tactic. Contact the institution through its official channel — never through the link or number given in the message."
    if category == "suspicious_link":
        return "This message contains a link that should not be opened without checking the destination and the sender independently."
    if category == "social_proof":
        return "Appeals to how many others have joined apply social pressure and are not evidence that an offer is genuine."
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