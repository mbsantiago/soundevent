"""Test the basic API of the io functions."""

import datetime
import json
from pathlib import Path

import pytest

from soundevent import data, io


def test_load_fails_if_file_does_not_exist():
    """Test that the load function fails if the file does not exist."""
    # Arrange
    path = "non_existing_file.json"

    # Act and assert
    with pytest.raises(FileNotFoundError):
        io.load(path)


def test_load_fails_if_file_is_not_a_json_file(tmp_path):
    """Test that the load function fails if the file is not a JSON file."""
    # Arrange
    path = tmp_path / "not_a_json_file.txt"
    path.touch()

    # Act and assert
    with pytest.raises(ValueError):
        io.load(path)


def test_load_fails_if_collection_type_is_not_supported(tmp_path):
    """Test that the load function fails if the collection type is not supported."""
    # Arrange
    path = tmp_path / "collection_type_not_supported.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "created_on": datetime.datetime.now().isoformat(),
                "data": {"collection_type": "not_supported"},
            }
        )
    )

    # Act and assert
    with pytest.raises(ValueError):
        io.load(path)


def test_load_fails_if_aoef_version_is_not_supported(tmp_path):
    """Test that the load function fails if the aoef version is not supported."""
    # Arrange
    path = tmp_path / "aoef_version_not_supported.json"
    path.write_text(
        json.dumps(
            {
                "version": 999,
                "created_on": datetime.datetime.now().isoformat(),
                "data": {"collection_type": "recording_set"},
            }
        )
    )

    # Act and assert
    with pytest.raises(ValueError):
        io.load(path)


def test_save_creates_parent_directories(
    tmp_path: Path, dataset: data.Dataset
):
    """Test that the save function creates parent directories."""
    # Arrange
    path = tmp_path / "parent" / "child" / "test.json"

    assert not path.parent.exists()

    # Act
    io.save(dataset, path)

    # Assert
    assert path.parent.exists()
    assert path.exists()


def test_save_fails_if_trying_to_save_unsupported_collection_type(
    tmp_path: Path,
    clip_evaluation: data.ClipEvaluation,
):
    """Test that the save function fails if trying to save an unsupported collection type."""
    # Arrange
    path = tmp_path / "unsupported_collection_type.json"

    # Act and assert
    with pytest.raises(NotImplementedError):
        io.save(clip_evaluation, path)  # type: ignore
