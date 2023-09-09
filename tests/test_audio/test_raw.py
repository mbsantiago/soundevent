"""Test suite for the RawData class."""

from pathlib import Path

import pytest
import soundfile as sf
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from soundevent.audio.chunks import parse_into_chunks
from soundevent.audio.raw import RawData


def test_raw_data_chunk_has_correct_number_of_channels(random_wav):
    """Test that the RawData chunk has the correct number of channels."""
    # Arrange
    samplerate = 16_000
    duration = 1
    channels = 2
    path = random_wav(
        samplerate=samplerate,
        duration=duration,
        channels=channels,
    )

    # Act
    with open(path, "rb") as fp:
        chunks = parse_into_chunks(fp)
        data = RawData(fp, chunks.subchunks["data"])

        with sf.SoundFile(
            data,
            samplerate=samplerate,
            channels=channels,
            subtype="FLOAT",
            format="RAW",
        ) as fp:
            assert fp.channels == 2


def test_raw_data_chunk_has_correct_size(random_wav):
    """Test that the RawData chunk has the correct size."""
    # Arrange
    samplerate = 16_000
    duration = 1
    channels = 2
    path = random_wav(
        samplerate=samplerate,
        duration=duration,
        channels=channels,
    )

    # Act
    with open(path, "rb") as fp:
        chunks = parse_into_chunks(fp)
        data = RawData(fp, chunks.subchunks["data"])

        with sf.SoundFile(
            data,
            samplerate=samplerate,
            channels=channels,
            subtype="FLOAT",
            format="RAW",
        ) as fp:
            assert len(fp) == int(samplerate * duration)
