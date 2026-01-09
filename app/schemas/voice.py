from datetime import datetime
from pydantic import BaseModel, Field


class VoiceRegisterResponse(BaseModel):
    person_id: str
    embedding_shape: list[int]
    registered_at: datetime
    file_path: str


class VoiceInfoResponse(BaseModel):
    person_id: str
    embedding_shape: list[int]
    registered_at: datetime
    file_size_bytes: int


class VoiceListResponse(BaseModel):
    person_id: str
    registered_at: datetime


class VoicesListResponse(BaseModel):
    voices: list[VoiceListResponse]
    total: int


class VoiceDeleteResponse(BaseModel):
    deleted: bool
    person_id: str
