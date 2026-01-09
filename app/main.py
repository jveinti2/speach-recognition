import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState
from app.config import settings
from app.dependencies import get_model_manager
from app.api.v1 import voices, sessions
from app.api.v1.sessions import get_audio_buffer, get_protocol_handler
from app.websocket.connection_manager import ConnectionManager
from app.websocket.audiohook_handler import AudioHookHandler
from app.websocket.audiohook_protocol import AudioHookProtocolHandler
from app.repositories.voice_repository import VoiceRepository

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="API REST + WebSocket para reconocimiento de voz con Genesys Cloud AudioHook"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voices.router, prefix="/api/v1")
app.include_router(sessions.router, prefix="/api/v1")

connection_manager = ConnectionManager()
voice_repository = VoiceRepository()
audio_buffer = get_audio_buffer()
protocol_handler = get_protocol_handler()

audiohook_handler = AudioHookHandler(
    audio_buffer,
    connection_manager,
    voice_repository
)


@app.on_event("startup")
async def startup_event():
    print(f"Iniciando {settings.APP_NAME} v{settings.VERSION}")
    model_mgr = get_model_manager()
    model_mgr.get_classifier()
    print("Modelo ECAPA-TDNN precargado exitosamente")
    print("WebSocket endpoint disponible en: ws://localhost:8000/ws/audiohook")


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": True,
        "version": settings.VERSION
    }


@app.websocket("/ws/audiohook")
async def websocket_audiohook(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    session = protocol_handler.create_session(session_id)
    print(f"WebSocket conectado: {session_id}")

    try:
        while True:
            message = await websocket.receive()

            if message["type"] == "websocket.disconnect":
                break

            if "text" in message:
                should_continue = await protocol_handler.handle_message(
                    websocket,
                    message["text"],
                    session
                )
                if not should_continue:
                    break

            elif "bytes" in message:
                audio_data = message["bytes"]
                if protocol_handler.handle_audio_frame(audio_data, session):
                    conversation_id = session.conversation_id
                    if conversation_id:
                        duration = audio_buffer.get_accumulated_duration(conversation_id)
                        if duration >= settings.TARGET_DURATION_SEC:
                            await audiohook_handler.identify_speaker(conversation_id)

    except WebSocketDisconnect:
        print(f"WebSocket desconectado: {session_id}")
    except Exception as e:
        print(f"Error en WebSocket: {str(e)}")
    finally:
        if session.conversation_id:
            audio_buffer.delete_session(session.conversation_id)
        protocol_handler.delete_session(session_id)
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()
