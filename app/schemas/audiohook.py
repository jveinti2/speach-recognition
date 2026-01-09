from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from enum import Enum


class ClientMessageType(str, Enum):
    OPEN = "open"
    CLOSE = "close"
    PING = "ping"
    DISCARDED = "discarded"
    DTMF = "dtmf"
    ERROR = "error"
    PLAYBACK_STARTED = "playback_started"
    PLAYBACK_COMPLETED = "playback_completed"


class ServerMessageType(str, Enum):
    OPENED = "opened"
    CLOSED = "closed"
    PONG = "pong"
    DISCONNECT = "disconnect"
    EVENT = "event"
    PAUSE = "pause"
    RESUME = "resume"
    UPDATE = "update"


class MediaFormat(str, Enum):
    PCMU = "PCMU"
    L16 = "L16"


class MediaConfig(BaseModel):
    type: str = "audio"
    format: MediaFormat = MediaFormat.PCMU
    channels: List[str] = ["external"]
    rate: int = 8000


class ParticipantInfo(BaseModel):
    id: str
    ani: Optional[str] = None
    dnis: Optional[str] = None
    name: Optional[str] = None


class OpenParameters(BaseModel):
    organizationId: str
    conversationId: str
    participant: Optional[ParticipantInfo] = None
    media: List[MediaConfig] = []
    customConfig: Optional[Dict[str, Any]] = None


class OpenedParameters(BaseModel):
    startPaused: bool = True
    media: List[MediaConfig] = []


class CloseParameters(BaseModel):
    reason: Optional[str] = None
    code: Optional[int] = None


class PingParameters(BaseModel):
    rtt: Optional[int] = None


class AudioHookClientMessage(BaseModel):
    version: str = "2"
    type: ClientMessageType
    seq: int
    serverseq: int = 0
    id: str
    position: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None


class AudioHookServerMessage(BaseModel):
    version: str = "2"
    type: ServerMessageType
    seq: int
    clientseq: int
    id: str
    position: Optional[int] = None
    parameters: Optional[Dict[str, Any]] = None


class WebSocketSession(BaseModel):
    session_id: str
    conversation_id: Optional[str] = None
    organization_id: Optional[str] = None
    participant: Optional[ParticipantInfo] = None
    media: List[MediaConfig] = []
    client_seq: int = 0
    server_seq: int = 0
    is_open: bool = False
    is_active: bool = False


class IdentificationResult(BaseModel):
    conversation_id: str
    identified: bool
    person_id: Optional[str]
    score: float
    all_scores: Dict[str, float]
    threshold: float
    completed_at: datetime
    message: Optional[str] = None
