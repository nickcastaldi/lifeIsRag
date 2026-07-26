"""Pick the fastest available torch device: Apple Metal (MPS) > CUDA > CPU."""
import torch


def get_device() -> str:
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"
