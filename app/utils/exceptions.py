from fastapi import HTTPException


class VoiceAlreadyExistsError(HTTPException):
    def __init__(self, person_id: str):
        super().__init__(
            status_code=409,
            detail=f"Voz '{person_id}' ya registrada"
        )


class VoiceNotFoundError(HTTPException):
    def __init__(self, person_id: str):
        super().__init__(
            status_code=404,
            detail=f"Voz '{person_id}' no encontrada"
        )


class InvalidAudioError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=400,
            detail=f"Audio inválido: {message}"
        )


class SessionNotFoundError(HTTPException):
    def __init__(self, conversation_id: str):
        super().__init__(
            status_code=404,
            detail=f"Sesión '{conversation_id}' no encontrada"
        )
