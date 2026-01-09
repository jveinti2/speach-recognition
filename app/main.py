from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.dependencies import get_model_manager
from app.api.v1 import voices, sessions
from app.api.v1.sessions import get_audio_buffer
from app.websocket.connection_manager import ConnectionManager
from app.websocket.audiohook_handler import AudioHookHandler
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
audiohook_handler = AudioHookHandler(
    get_audio_buffer(),
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
    await connection_manager.connect(websocket, "audiohook")
    try:
        while True:
            data = await websocket.receive_json()
            await audiohook_handler.process_audio_message(data)
    except WebSocketDisconnect:
        connection_manager.disconnect("audiohook")
        print("Cliente AudioHook desconectado")
    except Exception as e:
        print(f"Error en WebSocket: {str(e)}")
        connection_manager.disconnect("audiohook")
