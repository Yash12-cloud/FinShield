from backend.detection.patterns import find_red_flags, extract_registration_claims

def detect(text: str):
    return find_red_flags(text)

def registration_claims(text: str):
    return extract_registration_claims(text)
