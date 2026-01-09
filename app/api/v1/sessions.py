from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from app.schemas.session import (
    SessionActivateResponse,
    SessionPauseRequest,
    SessionPauseResponse,
    ActiveSessionsResponse
)
from app.services.session_service import SessionService
from app.utils.audio_buffer import AudioBuffer
from app.websocket.audiohook_protocol import AudioHookProtocolHandler

router = APIRouter(prefix="/sessions", tags=["sessions"])

audio_buffer = AudioBuffer()
protocol_handler = AudioHookProtocolHandler(audio_buffer)
session_service = SessionService(audio_buffer)


def get_audio_buffer() -> AudioBuffer:
    return audio_buffer


def get_protocol_handler() -> AudioHookProtocolHandler:
    return protocol_handler


def get_session_service() -> SessionService:
    return session_service


@router.post("/activate", response_model=SessionActivateResponse)
async def activate_session(
    conversation_id: str = Query(..., min_length=1, description="ID de la conversación a activar"),
    threshold: float = Query(0.75, ge=0.0, le=1.0, description="Umbral de similitud"),
    timeout: float = Query(30.0, ge=5.0, le=60.0, description="Timeout en segundos"),
    service: SessionService = Depends(get_session_service)
):
    start_time = datetime.now()

    protocol_handler.activate_session(conversation_id)
    activation_result = service.activate_session(conversation_id, threshold)

    identification_result = await service.wait_for_identification(conversation_id, timeout)

    if identification_result is None:
        raise HTTPException(
            status_code=408,
            detail=f"Timeout: no se recibió suficiente audio en {timeout}s"
        )

    processing_time = (datetime.now() - start_time).total_seconds()

    return SessionActivateResponse(
        conversation_id=conversation_id,
        status=activation_result["status"],
        activated_at=activation_result["activated_at"],
        identified=identification_result.get("identified", False),
        person_id=identification_result.get("person_id"),
        score=identification_result.get("score", 0.0),
        processing_time_seconds=processing_time
    )


@router.post("/pause", response_model=SessionPauseResponse)
async def pause_session(request: SessionPauseRequest, service: SessionService = Depends(get_session_service)):
    result = service.pause_session(request.conversation_id)
    return SessionPauseResponse(**result)


@router.get("/active", response_model=ActiveSessionsResponse)
async def get_active_sessions(service: SessionService = Depends(get_session_service)):
    sessions = service.get_active_sessions()
    return ActiveSessionsResponse(sessions=sessions, total=len(sessions))
