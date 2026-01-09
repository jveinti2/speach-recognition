import numpy as np
from numpy.linalg import norm
from app.config import settings


class VoiceMatcher:
    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (norm(a) * norm(b)))

    @staticmethod
    def find_match(embedding: np.ndarray, voice_pool: dict[str, np.ndarray], threshold: float = None) -> dict:
        if threshold is None:
            threshold = settings.DEFAULT_THRESHOLD

        if not voice_pool:
            return {
                "identified": False,
                "person_id": None,
                "score": 0.0,
                "all_scores": {},
                "message": "BD vacía - no hay voces registradas"
            }

        scores = {}
        for name, emb in voice_pool.items():
            scores[name] = VoiceMatcher.cosine_similarity(embedding, emb)

        best_match = max(scores, key=scores.get)
        best_score = scores[best_match]

        if best_score >= threshold:
            return {
                "identified": True,
                "person_id": best_match,
                "score": best_score,
                "all_scores": scores,
                "threshold": threshold
            }
        else:
            return {
                "identified": False,
                "person_id": None,
                "score": best_score,
                "all_scores": scores,
                "threshold": threshold,
                "message": f"Desconocido (mejor score={best_score:.3f})"
            }
