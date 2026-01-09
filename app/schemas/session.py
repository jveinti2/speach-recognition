from datetime import datetime
from pydantic import BaseModel, Field


class SessionActivateRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1)
    threshold: float = Field(0.75, ge=0.0, le=1.0)


class SessionActivateResponse(BaseModel):
    conversation_id: str
    status: str
    activated_at: datetime


class SessionPauseRequest(BaseModel):
    conversation_id: str = Field(..., min_length=1)


class SessionPauseResponse(BaseModel):
    conversation_id: str
    status: str


class ActiveSessionResponse(BaseModel):
    conversation_id: str
    threshold: float
    activated_at: datetime
    audio_duration_seconds: float


class ActiveSessionsResponse(BaseModel):
    sessions: list[ActiveSessionResponse]
    total: int
