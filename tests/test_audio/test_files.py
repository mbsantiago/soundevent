"""Test suite for audio.files module."""

from pathlib import Path

import pytest

from soundevent.audio import get_audio_files, is_audio_file


def test_text_file_is_not_audio(tmp_path: Path):
    """Test that text files are not considered audio files."""
    test_file = tmp_path / "test_files.txt"
    test_file.write_text("This is a test file.")
    assert test_file.is_file()
    assert not is_audio_file(test_file)


@pytest.mark.parametrize(
    "extension",
    [
        "aiff",
        "au",
        "avr",
        "caf",
        "flac",
        "htk",
        "ircam",
        "mat4",
        "mat5",
        "mp3",
        "mpc2k",
        "nist",
        "ogg",
        "paf",
        "pvf",
        "rf64",
        "sds",
        "svx",
        "voc",
        "w64",
        "wav",
        "wavex",
        "wve",
    ],
)
def test_files_with_valid_extensions_are_audio_files(
    tmp_path: Path, extension: str
):
    """Test that files with valid extensions are considered audio files."""
    test_file = tmp_path / f"test_files.{extension}"
    test_file.touch()
    assert test_file.is_file()
    assert is_audio_file(test_file)


@pytest.mark.parametrize(
    "extension",
    [
        "txt",
        "csv",
        "avi",
        "mp4",
        "jpg",
        "json",
        "py",
    ],
)
def test_files_with_invalid_extensions_are_not_audio_files(
    tmp_path: Path, extension: str
):
    """Test that files with invalid extensions are not considered audio files."""
    test_file = tmp_path / f"test_files.{extension}"
    test_file.touch()
    assert test_file.is_file()
    assert not is_audio_file(test_file)


def test_non_existing_files_are_not_audio():
    """Test that non-existing files are not considered audio files."""
    assert not is_audio_file("tests/test_audio/test_files.wav")


def test_mp3_audio_files_are_valid_audio_files():
    """Test that mp3 files are not considered audio files."""
    assert is_audio_file("tests/test_audio/data/mp3_mpeg_layer_iii.mp3")


def test_wav_files_are_considered_audio_files(random_wav):
    """Test that wav files are considered audio files."""
    path = random_wav()
    assert is_audio_file(path)
    assert is_audio_file(path, strict=True)


def test_strict_is_audio_file_for_non_audio_files(tmp_path: Path):
    """Test that is_audio_file returns False for non-audio files in strict mode."""
    path = tmp_path / "test_files.wav"
    path.touch()
    assert is_audio_file(path)
    assert not is_audio_file(path, strict=True)


def test_get_files_fails_if_not_a_directory(tmp_path: Path):
    """Test that get_files fails if the path is not a directory."""
    path = tmp_path / "test_files.wav"
    path.touch()

    with pytest.raises(ValueError):
        for _ in get_audio_files(path):
            pass


def test_get_files_returns_generator(tmp_path: Path):
    """Test that get_files returns a generator."""
    for _ in get_audio_files(tmp_path):
        pass


def test_get_files_does_not_get_nested_files_if_non_recursive(
    random_wav,
    tmp_path: Path,
):
    """Test that get_files does not get nested files if non-recursive."""
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()

    random_wav(path=tmp_path / "audio1.wav")
    random_wav(path=nested_dir / "audio2.wav")

    files = list(get_audio_files(tmp_path, recursive=False))
    assert len(files) == 1
    assert files == [tmp_path / "audio1.wav"]


def test_get_files_gets_nested_files_if_recursive(
    random_wav,
    tmp_path: Path,
):
    """Test that get_files gets nested files if recursive."""
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()

    random_wav(path=tmp_path / "audio1.wav")
    random_wav(path=nested_dir / "audio2.wav")

    files = list(get_audio_files(tmp_path, recursive=True))
    assert len(files) == 2
    assert tmp_path / "audio1.wav" in files
    assert nested_dir / "audio2.wav" in files


def test_get_files_does_not_include_non_audio_files(
    random_wav,
    tmp_path: Path,
):
    """Test that get_files does not include non-audio files."""
    random_wav(path=tmp_path / "audio1.wav")
    tmp_path.joinpath("test_files.txt").write_text("This is a test file.")

    files = list(get_audio_files(tmp_path))
    assert len(files) == 1
    assert files == [tmp_path / "audio1.wav"]


def test_get_files_excludes_invalid_audio_files_if_strict(
    random_wav,
    tmp_path: Path,
):
    """Test that get_files excludes invalid audio files."""
    random_wav(path=tmp_path / "audio1.wav")
    tmp_path.joinpath("invalid_audio.wav").write_text("This is a test file.")

    files = list(get_audio_files(tmp_path, strict=True))
    assert len(files) == 1
    assert files == [tmp_path / "audio1.wav"]

    files = list(get_audio_files(tmp_path, strict=False))
    assert len(files) == 2
    assert tmp_path / "invalid_audio.wav" in files
    assert tmp_path / "audio1.wav" in files
