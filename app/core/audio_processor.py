import torch
import torchaudio
from app.config import settings


class AudioProcessor:
    @staticmethod
    def load_and_normalize(file_path: str) -> tuple[torch.Tensor, int]:
        waveform, sr = torchaudio.load(file_path)

        if sr != settings.SAMPLE_RATE:
            raise ValueError(f"Sample rate debe ser {settings.SAMPLE_RATE}Hz, recibido: {sr}Hz")

        duration = waveform.shape[1] / sr
        if duration < settings.MIN_DURATION_SEC:
            raise ValueError(f"Audio muy corto: {duration:.1f}s (mínimo {settings.MIN_DURATION_SEC}s)")
        if duration > settings.MAX_DURATION_SEC:
            raise ValueError(f"Audio muy largo: {duration:.1f}s (máximo {settings.MAX_DURATION_SEC}s)")

        if waveform.shape[0] > 2:
            raise ValueError("Máximo 2 canales permitidos")

        waveform = waveform.mean(dim=0, keepdim=True)

        waveform = waveform / torch.max(torch.abs(waveform))

        return waveform, sr

    @staticmethod
    def validate_wav(file_path: str) -> tuple[torch.Tensor, int]:
        return AudioProcessor.load_and_normalize(file_path)
