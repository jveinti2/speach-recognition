import os
from typing import Dict, List
from datetime import datetime
from app.core.audio_processor import AudioProcessor
from app.core.embedding_generator import EmbeddingGenerator
from app.repositories.voice_repository import VoiceRepository
from app.dependencies import get_model_manager


class VoiceService:
    def __init__(self, voice_repository: VoiceRepository):
        self.voice_repository = voice_repository
        self.audio_processor = AudioProcessor()

        model_manager = get_model_manager()
        classifier = model_manager.get_classifier()
        self.embedding_generator = EmbeddingGenerator(classifier)

    def register_voice(self, audio_path: str, person_id: str) -> dict:
        if self.voice_repository.exists(person_id):
            raise FileExistsError(f"Voz '{person_id}' ya existe")

        waveform, sr = self.audio_processor.load_and_normalize(audio_path)

        embedding = self.embedding_generator.generate_embedding(waveform)

        file_path = self.voice_repository.save(person_id, embedding)

        return {
            "person_id": person_id,
            "embedding_shape": list(embedding.shape),
            "registered_at": datetime.now(),
            "file_path": file_path
        }

    def get_voice_info(self, person_id: str) -> dict:
        voice_data = self.voice_repository.get(person_id)

        file_path = voice_data["file_path"]
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        return {
            "person_id": person_id,
            "embedding_shape": list(voice_data["embedding"].shape),
            "registered_at": voice_data["registered_at"],
            "file_size_bytes": file_size
        }

    def list_voices(self) -> List[dict]:
        return self.voice_repository.list_all()

    def delete_voice(self, person_id: str) -> dict:
        self.voice_repository.delete(person_id)

        return {
            "deleted": True,
            "person_id": person_id
        }
