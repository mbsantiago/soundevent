"""Pytest fixtures for the audio tests."""
import random
import string
from pathlib import Path
from typing import Optional
from uuid import uuid4

import numpy as np
import pytest
from scipy.io import wavfile

from soundevent import data


def get_random_string(length):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


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


@pytest.fixture
def recording(random_wav) -> data.Recording:
    """Return a random recording."""
    path = random_wav()
    return data.Recording.from_file(path=path)


@pytest.fixture
def clip(recording: data.Recording) -> data.Clip:
    """Return a random clip."""
    return data.Clip(
        recording=recording,
        start_time=0.0,
        end_time=0.1,
    )


@pytest.fixture
def sound_event(recording: data.Recording) -> data.SoundEvent:
    """Return a random sound event."""
    return data.SoundEvent(
        recording=recording,
        geometry=data.BoundingBox(coordinates=[0.02, 2000, 0.08, 4000]),
    )


@pytest.fixture
def annotation(sound_event: data.SoundEvent) -> data.Annotation:
    """Return a random annotation."""
    return data.Annotation(
        sound_event=sound_event,
    )


@pytest.fixture
def predicted_sound_event(
    sound_event: data.SoundEvent,
) -> data.PredictedSoundEvent:
    """Return a random predicted sound event."""
    return data.PredictedSoundEvent(
        sound_event=sound_event,
        score=0.5,
    )


@pytest.fixture
def random_tags():
    """Generate a random list of tags for testing."""

    def factory(n=10):
        return [
            data.Tag(
                key=get_random_string(10),
                value=get_random_string(10),
            )
            for _ in range(n)
        ]

    return factory


@pytest.fixture
def random_clips(random_wav):
    """Generate a random list of clips for testing."""

    def factory(n=10, duration=0.1):
        return [
            data.Clip(
                recording=data.Recording.from_file(
                    path=random_wav(duration=duration),
                    compute_hash=False,
                ),
                start_time=0.0,
                end_time=duration,
            )
            for _ in range(n)
        ]

    return factory
