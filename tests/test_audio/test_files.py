"""Test suite for audio.files module."""

from soundevent.audio.files import is_audio_file


def test_text_file_is_not_audio():
    """Test that text files are not considered audio files."""
    assert not is_audio_file("tests/test_audio/test_files.txt")


def test_non_existing_files_are_not_audio():
    """Test that non-existing files are not considered audio files."""
    assert not is_audio_file("tests/test_audio/test_files.wav")


def test_mp3_audio_files_are_not_considered_audio():
    """Test that mp3 files are not considered audio files."""
    assert not is_audio_file("tests/test_audio/test_files.mp3")


def test_wav_files_are_considered_audio_files(random_wav):
    """Test that wav files are considered audio files."""
    path = random_wav()
    assert is_audio_file(path)
