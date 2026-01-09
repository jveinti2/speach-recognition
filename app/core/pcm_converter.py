import numpy as np
import torch
import torchaudio
from typing import List
from app.config import settings

ULAW_DECODE_TABLE = np.array([
    -32124, -31100, -30076, -29052, -28028, -27004, -25980, -24956,
    -23932, -22908, -21884, -20860, -19836, -18812, -17788, -16764,
    -15996, -15484, -14972, -14460, -13948, -13436, -12924, -12412,
    -11900, -11388, -10876, -10364,  -9852,  -9340,  -8828,  -8316,
     -7932,  -7676,  -7420,  -7164,  -6908,  -6652,  -6396,  -6140,
     -5884,  -5628,  -5372,  -5116,  -4860,  -4604,  -4348,  -4092,
     -3900,  -3772,  -3644,  -3516,  -3388,  -3260,  -3132,  -3004,
     -2876,  -2748,  -2620,  -2492,  -2364,  -2236,  -2108,  -1980,
     -1884,  -1820,  -1756,  -1692,  -1628,  -1564,  -1500,  -1436,
     -1372,  -1308,  -1244,  -1180,  -1116,  -1052,   -988,   -924,
      -876,   -844,   -812,   -780,   -748,   -716,   -684,   -652,
      -620,   -588,   -556,   -524,   -492,   -460,   -428,   -396,
      -372,   -356,   -340,   -324,   -308,   -292,   -276,   -260,
      -244,   -228,   -212,   -196,   -180,   -164,   -148,   -132,
      -120,   -112,   -104,    -96,    -88,    -80,    -72,    -64,
       -56,    -48,    -40,    -32,    -24,    -16,     -8,      0,
     32124,  31100,  30076,  29052,  28028,  27004,  25980,  24956,
     23932,  22908,  21884,  20860,  19836,  18812,  17788,  16764,
     15996,  15484,  14972,  14460,  13948,  13436,  12924,  12412,
     11900,  11388,  10876,  10364,   9852,   9340,   8828,   8316,
      7932,   7676,   7420,   7164,   6908,   6652,   6396,   6140,
      5884,   5628,   5372,   5116,   4860,   4604,   4348,   4092,
      3900,   3772,   3644,   3516,   3388,   3260,   3132,   3004,
      2876,   2748,   2620,   2492,   2364,   2236,   2108,   1980,
      1884,   1820,   1756,   1692,   1628,   1564,   1500,   1436,
      1372,   1308,   1244,   1180,   1116,   1052,    988,    924,
       876,    844,    812,    780,    748,    716,    684,    652,
       620,    588,    556,    524,    492,    460,    428,    396,
       372,    356,    340,    324,    308,    292,    276,    260,
       244,    228,    212,    196,    180,    164,    148,    132,
       120,    112,    104,     96,     88,     80,     72,     64,
        56,     48,     40,     32,     24,     16,      8,      0
], dtype=np.int16)


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
    def pcm_chunks_to_waveform(pcm_chunks: List[bytes], sample_rate: int = None) -> torch.Tensor:
        if not pcm_chunks:
            raise ValueError("Lista de chunks PCM vacía")

        concatenated = b''.join(pcm_chunks)

        return PCMConverter.pcm_to_waveform(concatenated, sample_rate)

    @staticmethod
    def ulaw_to_pcm(ulaw_bytes: bytes) -> bytes:
        ulaw_array = np.frombuffer(ulaw_bytes, dtype=np.uint8)
        pcm_array = ULAW_DECODE_TABLE[ulaw_array]
        return pcm_array.tobytes()

    @staticmethod
    def resample_8k_to_16k(pcm_bytes: bytes) -> bytes:
        audio_array = np.frombuffer(pcm_bytes, dtype=np.int16)
        audio_float = audio_array.astype(np.float32) / 32768.0
        waveform = torch.from_numpy(audio_float).unsqueeze(0)

        resampler = torchaudio.transforms.Resample(
            orig_freq=8000,
            new_freq=16000,
            dtype=waveform.dtype
        )
        resampled = resampler(waveform)

        resampled_int16 = (resampled.squeeze(0).numpy() * 32768.0).astype(np.int16)
        return resampled_int16.tobytes()

    @staticmethod
    def ulaw_chunks_to_waveform(ulaw_chunks: List[bytes]) -> torch.Tensor:
        if not ulaw_chunks:
            raise ValueError("Lista de chunks u-Law vacía")

        concatenated_ulaw = b''.join(ulaw_chunks)
        pcm_bytes = PCMConverter.ulaw_to_pcm(concatenated_ulaw)
        pcm_16k = PCMConverter.resample_8k_to_16k(pcm_bytes)

        return PCMConverter.pcm_to_waveform(pcm_16k, sample_rate=16000)
