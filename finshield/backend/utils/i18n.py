import json, os

_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "translations")
_cache = {}
SUPPORTED = ("en", "hi", "mr")
LANG_TAG = {"en": "en-IN", "hi": "hi-IN", "mr": "mr-IN"}


def load(locale: str) -> dict:
    locale = locale if locale in SUPPORTED else "en"
    if locale not in _cache:
        path = os.path.join(_DIR, locale + ".json")
        with open(path, encoding="utf-8") as f:
            _cache[locale] = json.load(f)
    return _cache[locale]


def localize_categories(categories, locale: str):
    """Return categories with label/explanation in the requested language.
    Falls back to the English strings when a translation is missing."""
    t = load(locale)
    cat_map = t.get("categories", {})
    out = []
    for c in categories:
        tr = cat_map.get(c["id"])
        first = c["matches"][0] if c["matches"] else "this claim"
        if tr:
            out.append({
                **c,
                "label": tr["label"],
                "explanation": tr["explanation"].replace("{first}", first),
            })
        else:
            out.append(c)
    return out


def localize_assessment_labels(locale: str) -> dict:
    return load(locale).get("assessment_labels", {})


def risk_text(level: str, locale: str) -> str:
    """Localized short risk descriptor, e.g. hi -> 'उच्च जोखिम'."""
    m = {"en": {"LOW CONCERN": "Low concern", "MODERATE CONCERN": "Moderate concern", "HIGH CONCERN": "High concern"},
         "hi": {"LOW CONCERN": "कम जोखिम", "MODERATE CONCERN": "मध्यम जोखिम", "HIGH CONCERN": "उच्च जोखिम"},
         "mr": {"LOW CONCERN": "कमी जोखीम", "MODERATE CONCERN": "मध्यम जोखीम", "HIGH CONCERN": "उच्च जोखीम"}}
    return m.get(locale, m["en"]).get(level, level)