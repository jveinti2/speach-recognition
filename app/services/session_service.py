from datetime import datetime
from app.utils.audio_buffer import AudioBuffer


class SessionService:
    def __init__(self, audio_buffer: AudioBuffer):
        self.audio_buffer = audio_buffer

    def activate_session(self, conversation_id: str, threshold: float = None) -> dict:
        self.audio_buffer.create_session(conversation_id, threshold)
        self.audio_buffer.activate(conversation_id)

        return {
            "conversation_id": conversation_id,
            "status": "active",
            "activated_at": datetime.now()
        }

    def pause_session(self, conversation_id: str) -> dict:
        self.audio_buffer.pause(conversation_id)

        return {
            "conversation_id": conversation_id,
            "status": "paused"
        }

    def get_active_sessions(self) -> list[dict]:
        return self.audio_buffer.get_active_sessions()
