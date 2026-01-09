import numpy as np
import torch
from app.config import settings


class PCMConverter:
    @staticmethod
    def pcm_to_waveform(pcm_bytes: bytes, sample_rate: int = None) -> torch.Tensor:
        if sample_rate is None:
            sample_rate = settings.SAMPLE_RATE

        audio_array = np.frombuffer(pcm_bytes, dtype=np.int16)

        audio_float = audio_array.astype(np.float32) / 32768.0

        waveform = torch.from_numpy(audio_float).unsqueeze(0)

        max_val = torch.max(torch.abs(waveform))
        if max_val > 0:
            waveform = waveform / max_val

        return waveform

    @staticmethod
    def pcm_chunks_to_waveform(pcm_chunks: list[bytes], sample_rate: int = None) -> torch.Tensor:
        if not pcm_chunks:
            raise ValueError("Lista de chunks PCM vacía")

        concatenated = b''.join(pcm_chunks)

        return PCMConverter.pcm_to_waveform(concatenated, sample_rate)
