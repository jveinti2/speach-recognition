import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.schemas.voice import (
    VoiceRegisterResponse,
    VoiceInfoResponse,
    VoicesListResponse,
    VoiceDeleteResponse
)
from app.services.voice_service import VoiceService
from app.repositories.voice_repository import VoiceRepository
from app.config import settings

router = APIRouter(prefix="/voices", tags=["voices"])

voice_repository = VoiceRepository()
voice_service = VoiceService(voice_repository)


def get_voice_service() -> VoiceService:
    return voice_service


@router.post("/register", response_model=VoiceRegisterResponse)
async def register_voice(
    audio: UploadFile = File(...),
    person_id: str = Form(...),
    service: VoiceService = Depends(get_voice_service)
):
    if not audio.filename.endswith('.wav'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos WAV")

    if not person_id or len(person_id.strip()) == 0:
        raise HTTPException(status_code=400, detail="person_id no puede estar vacío")

    person_id = person_id.strip()

    os.makedirs(settings.AUDIO_TMP, exist_ok=True)

    temp_path = os.path.join(settings.AUDIO_TMP, f"{uuid.uuid4()}.wav")

    try:
        with open(temp_path, "wb") as f:
            content = await audio.read()
            f.write(content)

        result = service.register_voice(temp_path, person_id)

        return VoiceRegisterResponse(**result)

    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.get("/list", response_model=VoicesListResponse)
async def list_voices(service: VoiceService = Depends(get_voice_service)):
    voices = service.list_voices()
    return VoicesListResponse(voices=voices, total=len(voices))


@router.get("/{person_id}", response_model=VoiceInfoResponse)
async def get_voice(person_id: str, service: VoiceService = Depends(get_voice_service)):
    try:
        voice_info = service.get_voice_info(person_id)
        return VoiceInfoResponse(**voice_info)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{person_id}", response_model=VoiceDeleteResponse)
async def delete_voice(person_id: str, service: VoiceService = Depends(get_voice_service)):
    try:
        result = service.delete_voice(person_id)
        return VoiceDeleteResponse(**result)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
