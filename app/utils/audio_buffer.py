from typing import List
from datetime import datetime
from app.config import settings

ULAW_SAMPLE_RATE = 8000


class AudioBuffer:
    def __init__(self):
        self._buffers = {}

    def create_session(self, conversation_id: str, threshold: float = None):
        if threshold is None:
            threshold = settings.DEFAULT_THRESHOLD

        self._buffers[conversation_id] = {
            "chunks": [],
            "sample_rate": ULAW_SAMPLE_RATE,
            "active": False,
            "threshold": threshold,
            "created_at": datetime.now()
        }

    def activate(self, conversation_id: str):
        if conversation_id not in self._buffers:
            self.create_session(conversation_id)

        self._buffers[conversation_id]["active"] = True
        self._buffers[conversation_id]["activated_at"] = datetime.now()

    def pause(self, conversation_id: str):
        if conversation_id in self._buffers:
            self._buffers[conversation_id]["active"] = False

    def append_chunk(self, conversation_id: str, pcm_data: bytes):
        if conversation_id in self._buffers and self._buffers[conversation_id]["active"]:
            self._buffers[conversation_id]["chunks"].append(pcm_data)

    def get_accumulated_duration(self, conversation_id: str) -> float:
        if conversation_id not in self._buffers:
            return 0.0

        chunks = self._buffers[conversation_id]["chunks"]
        sample_rate = self._buffers[conversation_id]["sample_rate"]

        if not chunks:
            return 0.0

        total_samples = sum(len(chunk) for chunk in chunks)

        duration = total_samples / sample_rate

        return duration

    def get_chunks(self, conversation_id: str) -> List[bytes]:
        if conversation_id not in self._buffers:
            return []

        return self._buffers[conversation_id]["chunks"]

    def get_threshold(self, conversation_id: str) -> float:
        if conversation_id not in self._buffers:
            return settings.DEFAULT_THRESHOLD

        return self._buffers[conversation_id]["threshold"]

    def clear(self, conversation_id: str):
        if conversation_id in self._buffers:
            self._buffers[conversation_id]["chunks"] = []

    def delete_session(self, conversation_id: str):
        if conversation_id in self._buffers:
            del self._buffers[conversation_id]

    def is_active(self, conversation_id: str) -> bool:
        if conversation_id not in self._buffers:
            return False

        return self._buffers[conversation_id]["active"]

    def get_active_sessions(self) -> List[dict]:
        result = []
        for conversation_id, data in self._buffers.items():
            if data["active"]:
                result.append({
                    "conversation_id": conversation_id,
                    "threshold": data["threshold"],
                    "activated_at": data.get("activated_at", data["created_at"]),
                    "audio_duration_seconds": self.get_accumulated_duration(conversation_id)
                })
        return result
