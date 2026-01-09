import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import torch
    from speechbrain.pretrained import EncoderClassifier


class EmbeddingGenerator:
    def __init__(self, classifier: "EncoderClassifier"):
        self.classifier = classifier

    def generate_embedding(self, waveform: "torch.Tensor") -> np.ndarray:
        import torch
        with torch.no_grad():
            embedding = self.classifier.encode_batch(waveform)

        embedding = embedding.squeeze().cpu().numpy()

        return embedding
