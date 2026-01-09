from fastapi import APIRouter, Depends
from app.schemas.session import (
    SessionActivateRequest,
    SessionActivateResponse,
    SessionPauseRequest,
    SessionPauseResponse,
    ActiveSessionsResponse
)
from app.services.session_service import SessionService
from app.utils.audio_buffer import AudioBuffer

router = APIRouter(prefix="/sessions", tags=["sessions"])

audio_buffer = AudioBuffer()
session_service = SessionService(audio_buffer)


def get_audio_buffer() -> AudioBuffer:
    return audio_buffer


def get_session_service() -> SessionService:
    return session_service


@router.post("/activate", response_model=SessionActivateResponse)
async def activate_session(request: SessionActivateRequest, service: SessionService = Depends(get_session_service)):
    result = service.activate_session(request.conversation_id, request.threshold)
    return SessionActivateResponse(**result)


@router.post("/pause", response_model=SessionPauseResponse)
async def pause_session(request: SessionPauseRequest, service: SessionService = Depends(get_session_service)):
    result = service.pause_session(request.conversation_id)
    return SessionPauseResponse(**result)


@router.get("/active", response_model=ActiveSessionsResponse)
async def get_active_sessions(service: SessionService = Depends(get_session_service)):
    sessions = service.get_active_sessions()
    return ActiveSessionsResponse(sessions=sessions, total=len(sessions))
