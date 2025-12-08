"""Tests for deterministic UUID generation."""

import uuid
from pathlib import Path

import pytest

from soundevent.data.clips import Clip
from soundevent.data.recordings import Recording
from soundevent.data.uuids import generate_clip_uuid, generate_recording_uuid


@pytest.fixture
def mock_recording_uuid():
    return uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest.fixture
def mock_recording(mock_recording_uuid):
    return Recording(
        uuid=mock_recording_uuid,
        path=Path("/path/to/audio.wav"),
        duration=10.0,
        channels=1,
        samplerate=44100,
        hash="test_hash_123",
    )


class TestUUIDGeneration:
    """Tests for the UUID generation logic."""

    def test_recording_uuid_deterministic(self):
        # GIVEN the same hash string
        hash_value = "my_unique_recording_hash"

        # WHEN generate_recording_uuid is called multiple times
        uuid1 = generate_recording_uuid(hash_value)
        uuid2 = generate_recording_uuid(hash_value)

        # THEN it should produce the exact same UUID.
        assert uuid1 == uuid2

    def test_recording_uuid_distinct(self):
        # GIVEN different hash strings
        hash_value1 = "my_unique_recording_hash_1"
        hash_value2 = "my_unique_recording_hash_2"

        # WHEN generate_recording_uuid is called
        uuid1 = generate_recording_uuid(hash_value1)
        uuid2 = generate_recording_uuid(hash_value2)

        # THEN it should produce different UUIDs.
        assert uuid1 != uuid2

    def test_recording_uuid_random_fallback(self):
        # GIVEN None as hash
        # WHEN generate_recording_uuid is called multiple times
        uuid1 = generate_recording_uuid(None)
        uuid2 = generate_recording_uuid(None)

        # THEN it should produce different random UUIDs each time.
        assert uuid1 != uuid2
        assert isinstance(uuid1, uuid.UUID)
        assert isinstance(uuid2, uuid.UUID)

    def test_clip_uuid_deterministic(self, mock_recording_uuid):
        # GIVEN the same recording UUID, start time, and end time
        start_time = 0.5
        end_time = 2.5

        # WHEN generate_clip_uuid is called multiple times
        uuid1 = generate_clip_uuid(mock_recording_uuid, start_time, end_time)
        uuid2 = generate_clip_uuid(mock_recording_uuid, start_time, end_time)

        # THEN it should produce the exact same UUID.
        assert uuid1 == uuid2

    def test_clip_uuid_sensitivity(self, mock_recording_uuid):
        # GIVEN slightly different parameters
        # WHEN generate_clip_uuid is called
        # THEN it should produce different UUIDs.
        uuid_base = generate_clip_uuid(mock_recording_uuid, 0.5, 2.5)

        # Different recording UUID
        diff_rec_uuid = uuid.UUID("00000000-0000-0000-0000-000000000002")
        uuid_diff_rec = generate_clip_uuid(diff_rec_uuid, 0.5, 2.5)
        assert uuid_base != uuid_diff_rec

        # Different start time
        uuid_diff_start = generate_clip_uuid(mock_recording_uuid, 0.6, 2.5)
        assert uuid_base != uuid_diff_start

        # Different end time
        uuid_diff_end = generate_clip_uuid(mock_recording_uuid, 0.5, 2.6)
        assert uuid_base != uuid_diff_end


class TestModelIntegration:
    """Tests for UUID integration in Pydantic models."""

    def test_recording_model_auto_uuid(self):
        # GIVEN a Recording object created with a hash but no explicit UUID

        # WHEN the object is instantiated
        recording = Recording(
            path=Path("/path/to/test.wav"),
            duration=5.0,
            channels=1,
            samplerate=44100,
            hash="some_deterministic_hash",
        )

        # THEN its UUID should be deterministically derived from the hash.
        expected_uuid = generate_recording_uuid("some_deterministic_hash")
        assert recording.uuid == expected_uuid

    def test_recording_model_explicit_uuid_respected(self):
        # GIVEN a Recording object created with an explicit UUID and a hash
        explicit_uuid = uuid.UUID("12345678-1234-5234-1234-1234567890ab")

        # WHEN the object is instantiated
        recording = Recording(
            uuid=explicit_uuid,
            path=Path("/path/to/test_explicit.wav"),
            duration=5.0,
            channels=1,
            samplerate=44100,
            hash="some_other_hash",
        )

        # THEN the explicit UUID should be respected (not overwritten).
        assert recording.uuid == explicit_uuid

    def test_recording_model_random_uuid_if_no_hash(self):
        # GIVEN a Recording object created without a hash or explicit UUID
        # WHEN the object is instantiated
        recording1 = Recording(
            path=Path("/path/to/random1.wav"),
            duration=5.0,
            channels=1,
            samplerate=44100,
            hash=None,
        )
        recording2 = Recording(
            path=Path("/path/to/random2.wav"),
            duration=5.0,
            channels=1,
            samplerate=44100,
            hash=None,
        )

        # THEN its UUID should be random.
        assert isinstance(recording1.uuid, uuid.UUID)
        assert isinstance(recording2.uuid, uuid.UUID)
        assert recording1.uuid != recording2.uuid

    def test_clip_model_auto_uuid(self, mock_recording):
        # GIVEN a Clip object created without an explicit UUID
        # WHEN the object is instantiated
        clip = Clip(recording=mock_recording, start_time=1.0, end_time=3.0)

        # THEN its UUID should be deterministically derived from recording and
        # times.
        expected_uuid = generate_clip_uuid(mock_recording.uuid, 1.0, 3.0)
        assert clip.uuid == expected_uuid

    def test_clip_model_explicit_uuid_respected(self, mock_recording):
        # GIVEN a Clip object created with an explicit UUID
        explicit_uuid = uuid.UUID("abcdefab-cdef-4cde-8901-abcdef123456")

        # WHEN the object is instantiated
        clip = Clip(
            uuid=explicit_uuid,
            recording=mock_recording,
            start_time=1.0,
            end_time=3.0,
        )

        # THEN the explicit UUID should be respected (not overwritten).
        assert clip.uuid == explicit_uuid
