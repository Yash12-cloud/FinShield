import json, os

_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "translations")
_cache = {}
SUPPORTED = ("en", "hi", "mr")


def load(locale: str) -> dict:
    locale = locale if locale in SUPPORTED else "en"
    if locale not in _cache:
        path = os.path.join(_DIR, locale + ".json")
        with open(path, encoding="utf-8") as f:
            _cache[locale] = json.load(f)
    return _cache[locale]