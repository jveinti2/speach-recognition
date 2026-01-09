import json
from typing import Dict, Optional, Any
from fastapi import WebSocket
from app.schemas.audiohook import (
    ClientMessageType,
    ServerMessageType,
    AudioHookServerMessage,
    WebSocketSession,
    MediaConfig,
    MediaFormat,
    OpenParameters,
    ParticipantInfo
)
from app.utils.audio_buffer import AudioBuffer


class AudioHookProtocolHandler:
    def __init__(self, audio_buffer: AudioBuffer):
        self.audio_buffer = audio_buffer
        self.sessions: Dict[str, WebSocketSession] = {}

    def create_session(self, session_id: str) -> WebSocketSession:
        session = WebSocketSession(session_id=session_id)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[WebSocketSession]:
        return self.sessions.get(session_id)

    def get_session_by_conversation(self, conversation_id: str) -> Optional[WebSocketSession]:
        for session in self.sessions.values():
            if session.conversation_id == conversation_id:
                return session
        return None

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def _increment_server_seq(self, session: WebSocketSession) -> int:
        session.server_seq += 1
        return session.server_seq

    def _build_response(
        self,
        session: WebSocketSession,
        msg_type: ServerMessageType,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        seq = self._increment_server_seq(session)
        response = AudioHookServerMessage(
            version="2",
            type=msg_type,
            seq=seq,
            clientseq=session.client_seq,
            id=session.session_id,
            parameters=parameters
        )
        return response.model_dump(mode='json')

    async def handle_open(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
        session: WebSocketSession
    ) -> bool:
        try:
            session.client_seq = message.get("seq", 0)
            session_id = message.get("id", session.session_id)
            session.session_id = session_id

            params = message.get("parameters", {})

            session.conversation_id = params.get("conversationId")
            session.organization_id = params.get("organizationId")

            participant_data = params.get("participant")
            if participant_data:
                session.participant = ParticipantInfo(**participant_data)

            media_list = params.get("media", [])
            selected_media = []
            for m in media_list:
                if "external" in m.get("channels", []):
                    media_config = MediaConfig(
                        type=m.get("type", "audio"),
                        format=MediaFormat(m.get("format", "PCMU")),
                        channels=m.get("channels", ["external"]),
                        rate=m.get("rate", 8000)
                    )
                    selected_media.append(media_config)
                    break

            if not selected_media and media_list:
                first_media = media_list[0]
                selected_media.append(MediaConfig(
                    type=first_media.get("type", "audio"),
                    format=MediaFormat(first_media.get("format", "PCMU")),
                    channels=first_media.get("channels", ["external"]),
                    rate=first_media.get("rate", 8000)
                ))

            session.media = selected_media
            session.is_open = True

            if session.conversation_id:
                self.audio_buffer.create_session(session.conversation_id)
                print(f"[{session.conversation_id}] Sesión creada (pausada)")

            response_params = {
                "startPaused": True,
                "media": [m.model_dump() for m in selected_media]
            }

            response = self._build_response(
                session,
                ServerMessageType.OPENED,
                response_params
            )

            await websocket.send_json(response)
            print(f"[{session.session_id}] Handshake completado - conversationId: {session.conversation_id}")
            return True

        except Exception as e:
            print(f"Error en handle_open: {str(e)}")
            return False

    async def handle_ping(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
        session: WebSocketSession
    ):
        session.client_seq = message.get("seq", session.client_seq)

        response = self._build_response(session, ServerMessageType.PONG)
        await websocket.send_json(response)

    async def handle_close(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
        session: WebSocketSession
    ):
        session.client_seq = message.get("seq", session.client_seq)

        if session.conversation_id:
            self.audio_buffer.delete_session(session.conversation_id)

        response = self._build_response(
            session,
            ServerMessageType.CLOSED,
            {"reason": "normal"}
        )
        await websocket.send_json(response)

        session.is_open = False
        print(f"[{session.session_id}] Conexión cerrada")

    async def handle_message(
        self,
        websocket: WebSocket,
        text_data: str,
        session: WebSocketSession
    ) -> bool:
        try:
            message = json.loads(text_data)
            msg_type = message.get("type", "").lower()

            if msg_type == ClientMessageType.OPEN.value:
                return await self.handle_open(websocket, message, session)

            elif msg_type == ClientMessageType.PING.value:
                await self.handle_ping(websocket, message, session)
                return True

            elif msg_type == ClientMessageType.CLOSE.value:
                await self.handle_close(websocket, message, session)
                return False

            else:
                session.client_seq = message.get("seq", session.client_seq)
                return True

        except json.JSONDecodeError as e:
            print(f"Error parseando mensaje JSON: {str(e)}")
            return True
        except Exception as e:
            print(f"Error procesando mensaje: {str(e)}")
            return True

    def handle_audio_frame(self, audio_data: bytes, session: WebSocketSession) -> bool:
        if not session.is_open or not session.conversation_id:
            return False

        if not self.audio_buffer.is_active(session.conversation_id):
            return False

        self.audio_buffer.append_chunk(session.conversation_id, audio_data)
        return True

    def activate_session(self, conversation_id: str) -> bool:
        session = self.get_session_by_conversation(conversation_id)
        if session:
            session.is_active = True
            self.audio_buffer.activate(conversation_id)
            print(f"[{conversation_id}] Sesión activada para procesamiento")
            return True
        return False

    def get_conversation_id(self, session_id: str) -> Optional[str]:
        session = self.get_session(session_id)
        if session:
            return session.conversation_id
        return None
