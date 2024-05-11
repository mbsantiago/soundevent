from pathlib import Path
from typing import Optional

import numpy as np
import pytest

from soundevent.audio.io import audio_to_bytes, load_audio


def test_audio_to_bytes(sample_24_bit_audio: Path):
    original_bytes = sample_24_bit_audio.read_bytes()[44:]  # ignore header
    audio, sr = load_audio(sample_24_bit_audio)
    result_bytes = audio_to_bytes(audio, sr, bit_depth=24)
    assert len(result_bytes) == len(original_bytes)


@pytest.mark.parametrize("bit_depth", [8, 16, 24, 32])
@pytest.mark.parametrize("duration", [0.1, 0.2, 0.5])
@pytest.mark.parametrize("channels", [1, 2])
@pytest.mark.parametrize("samplerate", [8_000, 16_000, 22_050])
@pytest.mark.parametrize("dtype", [np.int16, np.int32, np.float32])
def test_audio_to_bytes_has_correct_length(
    bit_depth: int,
    duration: float,
    channels: int,
    samplerate: int,
    dtype: np.dtype,
):
    samples = int(duration * samplerate)
    array = np.random.random(
        size=[int(duration * samplerate), channels]
    ).astype(dtype)

    bytes_per_sample = (bit_depth // 8) * channels
    expected_bytes = samples * bytes_per_sample
    audio_bytes = audio_to_bytes(array, samplerate, bit_depth)
    assert len(audio_bytes) == expected_bytes


@pytest.mark.parametrize("bit_depth", [16, 24, 32])
@pytest.mark.parametrize("duration", [0.1, 0.2, 0.5])
@pytest.mark.parametrize("channels", [1, 2])
@pytest.mark.parametrize("samplerate", [16_000, 22_050])
@pytest.mark.parametrize("offset", [0, 1024])
@pytest.mark.parametrize("samples", [None, 1024])
def test_load_audio_has_correct_shape(
    bit_depth: int,
    duration: float,
    channels: int,
    samplerate: int,
    offset: int,
    samples: Optional[int],
    random_wav,
):
    path = random_wav(
        samplerate=samplerate,
        duration=duration,
        channels=channels,
        bit_depth=bit_depth,
    )

    array, _ = load_audio(path, offset=offset, samples=samples)

    if samples is None:
        total_samples = int(duration * samplerate)
        assert array.shape == (total_samples - offset, channels)

    else:
        assert array.shape == (samples, channels)


def test_audio_to_bytes_fails_with_invalid_bit_depth():
    array = np.random.random(size=[1024, 2])
    with pytest.raises(ValueError):
        audio_to_bytes(array, 16000, bit_depth=12)
