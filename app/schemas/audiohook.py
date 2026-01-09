from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field


class AudioHookMessage(BaseModel):
    conversation_id: str
    audio_data: str
    sample_rate: int = 16000
    timestamp: datetime


class IdentificationResult(BaseModel):
    conversation_id: str
    identified: bool
    person_id: Optional[str]
    score: float
    all_scores: Dict[str, float]
    threshold: float
    completed_at: datetime
    message: Optional[str] = None
