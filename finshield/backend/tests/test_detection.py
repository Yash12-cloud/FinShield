from backend.detection.red_flags import detect, registration_claims
from backend.detection.scoring import level

DEMO = """🚨 LIMITED TIME INVESTMENT OPPORTUNITY!

SEBI-approved investment plan — earn 30% guaranteed
returns every month with zero risk!

Only 10 slots remaining. Act NOW before registration
closes tonight!

Minimum investment: ₹10,000.

Send the amount to activate your account and join
our VIP Telegram group for daily guaranteed profit
signals.

SEBI Registration: INZ000XXXXX

Don't miss this opportunity — everyone is already joining!"""

SAFE = """SEBI has published investor education resources explaining basic risks associated with
investing in securities markets. Before investing, investors should understand the product,
read the relevant documents, and verify information using official sources. Investment
decisions should be based on your own research and understanding of the associated risks."""


def test_demo_message_grouped_categories():
    cats = detect(DEMO)
    ids = {c["id"] for c in cats}
    assert {"guaranteed_return", "urgency_fomo", "payment_pressure",
            "authority_impersonation", "social_group_migration"} <= ids
    urgency = next(c for c in cats if c["id"] == "urgency_fomo")
    assert len(urgency["matches"]) >= 3
    assert level(cats) == "HIGH CONCERN"


def test_education_message_clean():
    cats = detect(SAFE)
    assert cats == []
    assert level(cats) == "LOW CONCERN"


def test_demo_registration_is_flagged_for_verification_not_fraud():
    claims = registration_claims(DEMO)
    assert claims, "INZ placeholder should be surfaced for verification"
    assert claims[0]["status"] == "Requires independent verification"
    assert "placeholder" in claims[0]["reason"]


def test_impersonation_and_social_proof_and_link_detected():
    cats = detect("URGENT KYC: your account will be suspended. Update KYC here http://sebi-kyc.xyz. Thousands already invested!")
    ids = {c["id"] for c in cats}
    assert {"impersonation", "suspicious_link", "social_proof"} <= ids

def test_localization_hi_mr():
    from backend.utils.i18n import localize_categories, localize_assessment_labels
    cats = detect(DEMO)
    hi = localize_categories(cats, "hi")
    assert any(any("\u0900" <= ch <= "\u097F" for ch in c["label"]) for c in hi)
    assert all(c["label"] for c in hi)
    assert localize_assessment_labels("mr").get("signals")


def test_fallback_is_localized():
    from backend.services.llm import _fallback
    for loc, needle in [("hi", "जोखिम"), ("mr", "जोखीम")]:
        out = _fallback({"risk_categories": [{"label": "x", "explanation": "y"}], "risk_level": "HIGH CONCERN"}, loc)
        assert needle in out["uncertainty"]
