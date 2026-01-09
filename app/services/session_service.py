import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from app.utils.audio_buffer import AudioBuffer
from app.config import settings


class SessionService:
    def __init__(self, audio_buffer: AudioBuffer):
        self.audio_buffer = audio_buffer
        self.identification_results: Dict[str, dict] = {}

    def activate_session(self, conversation_id: str, threshold: float = None) -> dict:
        self.audio_buffer.create_session(conversation_id, threshold)
        self.audio_buffer.activate(conversation_id)

        return {
            "conversation_id": conversation_id,
            "status": "active",
            "activated_at": datetime.now()
        }

    async def wait_for_identification(
        self,
        conversation_id: str,
        timeout: float = 30.0
    ) -> Optional[dict]:
        start_time = datetime.now()

        while True:
            if conversation_id in self.identification_results:
                result = self.identification_results.pop(conversation_id)
                return result

            duration = self.audio_buffer.get_accumulated_duration(conversation_id)

            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed >= timeout:
                return None

            await asyncio.sleep(0.5)

    def store_identification_result(self, conversation_id: str, result: dict):
        self.identification_results[conversation_id] = result

    def pause_session(self, conversation_id: str) -> dict:
        self.audio_buffer.pause(conversation_id)

        return {
            "conversation_id": conversation_id,
            "status": "paused"
        }

    def get_active_sessions(self) -> List[dict]:
        return self.audio_buffer.get_active_sessions()
