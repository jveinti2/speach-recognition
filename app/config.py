import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Speech Recognition API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENV: str = "production"

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_DIR: str = os.path.join(BASE_DIR, "models", "spkrec-ecapa-voxceleb")
    VOICES_DB: str = os.path.join(BASE_DIR, "voices_db")
    AUDIO_TMP: str = os.path.join(BASE_DIR, "audio_tmp")

    SAMPLE_RATE: int = 16000
    CHANNELS: int = 1
    MIN_DURATION_SEC: float = 8.0
    MAX_DURATION_SEC: float = 15.0
    TARGET_DURATION_SEC: float = 10.0
    MAX_FILE_SIZE_MB: int = 2

    DEFAULT_THRESHOLD: float = 0.75

    GENESYS_AUDIOHOOK_URL: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
