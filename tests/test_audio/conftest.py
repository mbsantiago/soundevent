"""Pytest fixtures for the audio tests."""
from pathlib import Path
from typing import Optional
from uuid import uuid4

import numpy as np
import pytest
from scipy.io import wavfile


def write_random_wav(
    path: Path,
    samplerate: int = 22100,
    duration: float = 0.1,
    channels: int = 1,
) -> None:
    """Write a random wav file to the given path."""
    frames = int(samplerate * duration)
    shape = (frames, channels)
    wav = np.random.random(size=shape).astype(np.float32)
    wavfile.write(path, samplerate, wav)


@pytest.fixture
def random_wav(tmp_path: Path):
    """Return a factory for random wav files."""

    def _random_wav(
        path: Optional[Path] = None,
        samplerate: int = 22100,
        duration: float = 0.1,
        channels: int = 1,
    ) -> Path:
        """Return a random wav file."""
        if path is None:
            path = tmp_path / f"{uuid4()}.wav"
        write_random_wav(path, samplerate, duration, channels)
        return path

    return _random_wav
