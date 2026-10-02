import os, json

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

from backend.utils.config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL

def explain(user_text: str, analysis: dict) -> dict:
    """LLM generates the user-facing explanation from structured analysis.
    Deterministic fallback when no key is configured."""
    if LLM_API_KEY and OpenAI:
        try:
            client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL or None)
            prompt = (
                "You are FinShield, an investor-protection explainer. From the structured analysis of a financial message, "
                "produce a JSON object with keys: explanation, verification_steps (list), safe_next_steps (list), uncertainty (string). "
                "Simple language, Hindi if the message is Hindi. No investment advice, no price predictions, no tips.\n\n"
                "Message: " + user_text + "\n\nAnalysis:\n" + json.dumps(analysis, default=str, ensure_ascii=False)
            )
            resp = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            content = resp.choices[0].message.content.strip()
            if content.startswith("```"):
                content = content.strip("`").replace("json\n", "", 1)
            start = content.find("{")
            if start > 0:
                content = content[start:]
            return json.JSONDecoder().raw_decode(content)[0]
        except Exception:
            pass
    return _fallback(analysis)

def _fallback(analysis: dict) -> dict:
    cats = analysis.get("risk_categories", [])
    if cats:
        flags_text = "; ".join(c["label"] + ": " + c["explanation"] for c in cats)
    else:
        flags_text = "No strong red flags detected."
    return {
        "explanation": "Risk level: " + analysis["risk_level"] + ". " + flags_text,
        "verification_steps": [
            "Verify the claimed entity on an official source (e.g. sebi.gov.in).",
            "Check the original source of the message.",
            "Look for independent evidence for the claims.",
        ],
        "safe_next_steps": [
            "Do not share OTPs, passwords, or UPI PINs.",
            "Do not transfer money based only on this message.",
            "Pause and reflect before acting.",
        ],
        "uncertainty": "This analysis identifies risk indicators and verification gaps. It does not determine with certainty that the content is fraudulent, and it is not investment advice.",
    }
