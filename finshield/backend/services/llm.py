import json

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

from backend.utils.config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL
from backend.utils.i18n import load as load_locale

LANG_NAME = {"en": "English", "hi": "Hindi", "mr": "Marathi"}

GUARDRAILS = (
    "You are FinShield, an investor-protection explainer. Explain the structured risk analysis to a "
    "first-time Indian investor in simple, everyday language. You must follow these rules strictly:\n"
    "- Never give investment advice, buy/sell/hold recommendations, price predictions, or stock tips.\n"
    "- Never state with certainty that the content is a scam; describe risk indicators and uncertainty.\n"
    "- Never invent risk indicators, evidence, or registration status that is not in the given analysis.\n"
    "- Do not override the provided deterministic findings; explain them.\n"
    "- Answer only in the requested language.\n\n"
    "Return ONLY a JSON object with keys: explanation (string), verification_steps (list of strings), "
    "safe_next_steps (list of strings), uncertainty (string)."
)


def explain(user_text: str, analysis: dict, locale: str = "en") -> dict:
    """LLM explains the structured analysis. Deterministic fallback if unavailable.
    The LLM never overrides deterministic rules — it only explains them."""
    if LLM_API_KEY and OpenAI:
        try:
            client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL or None)
            prompt = (
                GUARDRAILS
                + "\n\nLanguage: " + LANG_NAME.get(locale, "English")
                + "\n\nMessage:\n" + user_text
                + "\n\nStructured analysis:\n" + json.dumps(analysis, default=str, ensure_ascii=False)
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
            parsed = json.JSONDecoder().raw_decode(content)[0]
            if isinstance(parsed, dict) and parsed.get("explanation"):
                return parsed
        except Exception:
            pass
    return _fallback(analysis, locale)


def _fallback(analysis: dict, locale: str = "en") -> dict:
    t = load_locale(locale)
    cats = analysis.get("risk_categories", [])
    if cats and locale == "en":
        flags_text = " ".join(c["label"] + ": " + c["explanation"] for c in cats)
    else:
        flags_text = ""
    return {
        "explanation": (t["detected_intro"] + (" " + flags_text if flags_text else ""))
        if cats else t["no_flags"],
        "verification_steps": t["verification_steps"],
        "safe_next_steps": t["safe_next_steps"],
        "uncertainty": t["uncertainty"],
    }