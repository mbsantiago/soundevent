"""Test suite for saving and loading recording sets."""

from pathlib import Path

from soundevent import data, io


def test_recording_set_is_recovered(
    recording_set: data.RecordingSet,
    audio_dir: Path,
):
    """Test that the recording set is recovered."""
    # Arrange
    path = audio_dir / "recording_set.json"

    # Act
    io.save(recording_set, path, audio_dir=audio_dir)
    recovered = io.load(path, audio_dir=audio_dir)

    # Assert
    assert recovered == recording_set
