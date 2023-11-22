"""Test suite for AOEF Recording Adapter."""

from pathlib import Path

from soundevent import data
from soundevent.io.aoef.note import NoteAdapter
from soundevent.io.aoef.recording import RecordingAdapter, RecordingObject
from soundevent.io.aoef.tag import TagAdapter
from soundevent.io.aoef.user import UserAdapter


def test_recording_can_be_converted_to_aoef(
    recording: data.Recording,
    recording_adapter: RecordingAdapter,
):
    """Test that a recording can be converted to AOEF."""
    aoef = recording_adapter.to_aoef(recording)
    assert isinstance(aoef, RecordingObject)


def test_recording_is_recovered(
    recording: data.Recording,
    recording_adapter: RecordingAdapter,
):
    """Test that a recording is recovered."""
    aoef = recording_adapter.to_aoef(recording)
    recovered = recording_adapter.to_soundevent(aoef)
    assert recording == recovered


def test_relative_path_is_stored(
    audio_dir: Path,
    user_adapter: UserAdapter,
    tag_adapter: TagAdapter,
    note_adapter: NoteAdapter,
):
    """Test that a relative path is stored."""
    abs_path = (audio_dir / "audio.wav").resolve()

    assert abs_path.is_absolute()

    recording = data.Recording(
        path=abs_path,
        duration=1,
        samplerate=16_000,
        channels=1,
    )

    adapter = RecordingAdapter(
        user_adapter, tag_adapter, note_adapter, audio_dir=audio_dir
    )

    aoef = adapter.to_aoef(recording)
    assert aoef.path == Path("audio.wav")
