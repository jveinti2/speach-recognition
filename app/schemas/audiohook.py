from datetime import datetime
from pydantic import BaseModel, Field


class AudioHookMessage(BaseModel):
    conversation_id: str
    audio_data: str
    sample_rate: int = 16000
    timestamp: datetime


class IdentificationResult(BaseModel):
    conversation_id: str
    identified: bool
    person_id: str | None
    score: float
    all_scores: dict[str, float]
    threshold: float
    completed_at: datetime
    message: str | None = None
