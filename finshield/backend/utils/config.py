import os
from dotenv import load_dotenv

load_dotenv()

MERCURY_API_KEY = os.getenv("MERCURY_API_KEY", "")
MERCURY_BASE_URL = os.getenv("MERCURY_BASE_URL", "https://openrouter.ai/api/v1")
MERCURY_MODEL = os.getenv("MERCURY_MODEL", "inception/mercury-decide:free")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
