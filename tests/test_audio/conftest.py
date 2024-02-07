"""Common fixtures for audio tests."""

from pathlib import Path

import pytest

SAMPLE_AUDIO = Path(__file__).parent / "24bitdepth.wav"


@pytest.fixture
def sample_24_bit_audio() -> Path:
    """Return a Path object to a 24-bit WAV file."""
    return SAMPLE_AUDIO
