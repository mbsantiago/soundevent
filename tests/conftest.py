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
def user() -> data.User:
    """Return a user."""
    return data.User(
        name="test_user",
    )


@pytest.fixture
def note(user: data.User) -> data.Note:
    """Return a note."""
    return data.Note(
        message="test_note",
        created_by=user,
    )


@pytest.fixture
def audio_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for audio files."""
    audio_dir = tmp_path / "audio"
    if not audio_dir.exists():
        audio_dir.mkdir()
    return audio_dir


@pytest.fixture
def random_wav(audio_dir: Path):
    """Return a factory for random wav files."""

    def _random_wav(
        path: Optional[Path] = None,
        samplerate: int = 22100,
        duration: float = 0.1,
        channels: int = 1,
    ) -> Path:
        """Return a random wav file."""
        if path is None:
            path = audio_dir / f"{uuid4()}.wav"
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
def bounding_box() -> data.BoundingBox:
    """Return a bounding box."""
    return data.BoundingBox(coordinates=[0.0, 0.0, 1.0, 1.0])


@pytest.fixture
def sound_event(
    bounding_box: data.BoundingBox,
) -> data.SoundEvent:
    """Return a sound event."""
    return data.SoundEvent(geometry=bounding_box)


@pytest.fixture
def sound_event_annotation(
    sound_event: data.SoundEvent,
) -> data.SoundEventAnnotation:
    """Return a random annotation."""
    return data.SoundEventAnnotation(
        sound_event=sound_event,
    )


@pytest.fixture
def sound_event_prediction(
    sound_event: data.SoundEvent,
) -> data.SoundEventPrediction:
    """Return a random predicted sound event."""
    return data.SoundEventPrediction(
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
