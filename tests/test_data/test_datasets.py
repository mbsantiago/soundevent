"""Test suite for dataset functions."""

from pathlib import Path

import pytest

from soundevent import data


def test_can_create_dataset_from_empty_directory(tmp_path: Path):
    """Test that we can create an empty dataset."""
    dataset = data.Dataset.from_directory(tmp_path, name="test")
    assert len(dataset.recordings) == 0


def test_can_provide_name_and_description_to_dataset(tmp_path: Path):
    """Test that we can provide a name and description to the dataset."""
    dataset = data.Dataset.from_directory(
        tmp_path,
        name="test",
        description="test description",
    )
    assert dataset.name == "test"
    assert dataset.description == "test description"


def test_can_create_dataset_reads_audio_files(tmp_path: Path, random_wav):
    """Test that we can create a dataset from audio files."""
    random_wav(
        path=tmp_path / "test1.wav",
        duration=1.0,
        samplerate=44100,
        channels=1,
    )
    dataset = data.Dataset.from_directory(tmp_path, name="test")

    assert len(dataset.recordings) == 1
    assert dataset.recordings[0].path == tmp_path / "test1.wav"
    assert dataset.recordings[0].duration == 1.0
    assert dataset.recordings[0].samplerate == 44100
    assert dataset.recordings[0].channels == 1


def test_create_dataset_ignores_non_audio_files(tmp_path: Path):
    """Test that we can create a dataset from audio files."""
    (tmp_path / "test1.txt").touch()
    dataset = data.Dataset.from_directory(tmp_path, name="test")

    assert len(dataset.recordings) == 0


def test_create_dataset_fails_with_non_existing_directory():
    """Test that we can create a dataset from audio files."""
    with pytest.raises(ValueError):
        data.Dataset.from_directory(
            Path("non-existing-directory"), name="test"
        )


def test_create_dataset_fails_if_path_is_file(tmp_path: Path):
    """Test that we can create a dataset from audio files."""
    (tmp_path / "test1.wav").touch()
    with pytest.raises(ValueError):
        data.Dataset.from_directory(tmp_path / "test1.wav", name="test")


def test_create_dataset_is_recursive_by_default(tmp_path: Path, random_wav):
    """Test that we can create a dataset from audio files."""
    (tmp_path / "test1").mkdir()
    random_wav(path=tmp_path / "test1" / "test1.wav")
    dataset = data.Dataset.from_directory(tmp_path, name="test")

    assert len(dataset.recordings) == 1
    assert dataset.recordings[0].path == tmp_path / "test1" / "test1.wav"


def test_create_dataset_without_recursive(tmp_path: Path, random_wav):
    """Test that we can create a dataset from audio files."""
    (tmp_path / "test1").mkdir()
    random_wav(path=tmp_path / "test1" / "test1.wav")
    dataset = data.Dataset.from_directory(
        tmp_path, recursive=False, name="test"
    )

    assert len(dataset.recordings) == 0


def test_create_dataset_computes_hash_of_recordings_by_default(
    tmp_path: Path, random_wav
):
    """Test that we can create a dataset from audio files."""
    random_wav(path=tmp_path / "test1.wav")
    dataset = data.Dataset.from_directory(tmp_path, name="test")

    assert len(dataset.recordings) == 1
    assert dataset.recordings[0].hash is not None


def test_create_dataset_without_computing_hashes(tmp_path: Path, random_wav):
    """Test that we can create a dataset from audio files."""
    random_wav(path=tmp_path / "test1.wav")
    dataset = data.Dataset.from_directory(
        tmp_path,
        compute_hash=False,
        name="test",
    )

    assert len(dataset.recordings) == 1
    assert dataset.recordings[0].hash is None
