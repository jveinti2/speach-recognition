import os
import numpy as np
from typing import Dict, List
from datetime import datetime
from app.config import settings


class VoiceRepository:
    def __init__(self):
        self._cache = {}
        self._load_all_to_cache()

    def _load_all_to_cache(self):
        if not os.path.exists(settings.VOICES_DB):
            os.makedirs(settings.VOICES_DB, exist_ok=True)
            return

        for file in os.listdir(settings.VOICES_DB):
            if file.endswith('.npy'):
                person_id = file.replace('.npy', '')
                file_path = os.path.join(settings.VOICES_DB, file)
                self._cache[person_id] = {
                    "embedding": np.load(file_path),
                    "file_path": file_path,
                    "registered_at": datetime.fromtimestamp(os.path.getmtime(file_path))
                }

    def save(self, person_id: str, embedding: np.ndarray) -> str:
        file_path = os.path.join(settings.VOICES_DB, f"{person_id}.npy")

        if os.path.exists(file_path):
            raise FileExistsError(f"Voz '{person_id}' ya existe")

        np.save(file_path, embedding)

        self._cache[person_id] = {
            "embedding": embedding,
            "file_path": file_path,
            "registered_at": datetime.now()
        }

        return file_path

    def get(self, person_id: str) -> dict:
        if person_id not in self._cache:
            raise FileNotFoundError(f"Voz '{person_id}' no encontrada")

        return self._cache[person_id]

    def get_all_embeddings(self) -> Dict[str, np.ndarray]:
        return {person_id: data["embedding"] for person_id, data in self._cache.items()}

    def list_all(self) -> List[dict]:
        return [
            {
                "person_id": person_id,
                "registered_at": data["registered_at"],
                "embedding_shape": list(data["embedding"].shape)
            }
            for person_id, data in self._cache.items()
        ]

    def delete(self, person_id: str) -> bool:
        if person_id not in self._cache:
            raise FileNotFoundError(f"Voz '{person_id}' no encontrada")

        file_path = self._cache[person_id]["file_path"]

        if os.path.exists(file_path):
            os.remove(file_path)

        del self._cache[person_id]

        return True

    def exists(self, person_id: str) -> bool:
        return person_id in self._cache
