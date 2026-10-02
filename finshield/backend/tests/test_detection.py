from backend.detection.red_flags import detect
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

def test_demo_message_grouped_categories():
    cats = detect(DEMO)
    ids = {c["id"] for c in cats}
    assert {"guaranteed_return", "urgency_fomo", "payment_pressure", "authority_impersonation", "social_group_migration"} <= ids
    urgency = next(c for c in cats if c["id"] == "urgency_fomo")
    assert len(urgency["matches"]) >= 3  # grouped, not split into separate flags
    assert level(cats) == "HIGH CONCERN"

def test_education_message_clean():
    text = "Volatility means the value of an investment can move up and down over time. Diversification reduces risk."
    cats = detect(text)
    assert cats == []
    assert level(cats) == "LOW CONCERN"
