from pydantic import BaseModel
from typing import List, Any, Dict

class AnalyzeTextRequest(BaseModel):
    text: str

class AnalyzeResponse(BaseModel):
    risk_level: str
    content_type: str
    severity: str
    requires_verification: bool
    risk_categories: List[Dict[str, Any]]
    mercury: Dict[str, Any]
    evidence: Dict[str, Any]
    explanation: str
    verification_steps: List[str]
    safe_next_steps: List[str]
    uncertainty: str
