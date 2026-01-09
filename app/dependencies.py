from functools import lru_cache
from app.config import settings


class ModelManager:
    _instance = None
    _classifier = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_classifier(self):
        if self._classifier is None:
            from speechbrain.pretrained import EncoderClassifier
            self._classifier = EncoderClassifier.from_hparams(
                source=settings.MODEL_DIR,
                savedir=settings.MODEL_DIR,
                run_opts={"device": "cpu"}
            )
        return self._classifier


@lru_cache()
def get_model_manager() -> ModelManager:
    return ModelManager()
