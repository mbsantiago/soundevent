"""Test suite for loading and saving datasets."""

import datetime
import json
from pathlib import Path

from soundevent import data, io


def test_dataset_is_recovered(
    dataset: data.Dataset,
    audio_dir: Path,
):
    """Test that the dataset is recovered."""
    # Arrange
    path = audio_dir / "dataset.json"

    # Act
    io.save(dataset, path, audio_dir=audio_dir)
    recovered = io.load(path, audio_dir=audio_dir)

    # Assert
    assert recovered == dataset


def test_save_empty_dataset_to_aoef_format(tmp_path: Path):
    """Test saving a dataset to the AOEF format."""
    # Arrange
    path = tmp_path / "dataset.json"
    dataset = data.Dataset(
        name="test_dataset",
        description="A test dataset.",
        recordings=[],
    )

    # Act
    io.save(dataset, path, audio_dir=tmp_path)

    # Assert
    assert path.exists()
    assert path.is_file()
    content = json.loads(path.read_text())["data"]
    assert content["name"] == "test_dataset"
    assert content["description"] == "A test dataset."
    assert content["uuid"] == str(dataset.uuid)
    assert content["recordings"] == []
    assert "tags" not in content


def test_save_dataset_contains_datetime_of_creation(
    tmp_path: Path,
    monkeypatch,
):
    """Test saving a dataset to the AOEF format."""
    # Arrange
    path = tmp_path / "dataset.json"
    dataset = data.Dataset(
        name="test_dataset",
        description="A test dataset.",
        recordings=[],
    )

    fake_datetime = datetime.datetime(2023, 7, 14, 12, 0, 0)

    class MockDatetime(datetime.datetime):
        @classmethod
        def now(cls):  # type: ignore
            return fake_datetime

    monkeypatch.setattr(datetime, "datetime", MockDatetime)

    # Act
    io.save(dataset, path, audio_dir=tmp_path)

    # Assert
    assert path.exists()
    assert path.is_file()
    content = json.loads(path.read_text())
    assert "created_on" in content
    assert content["created_on"] == "2023-07-14T12:00:00"


def test_save_dataset_with_one_simple_recording(tmp_path: Path):
    """Test saving a dataset with one recording to the AOEF format."""
    # Arrange
    path = tmp_path / "dataset.json"
    dataset = data.Dataset(
        name="test_dataset",
        description="A test dataset.",
        recordings=[
            data.Recording(
                path=tmp_path / "audio.wav",
                duration=10.0,
                channels=1,
                samplerate=44100,
            )
        ],
    )

    # Act
    io.save(dataset, path, audio_dir=tmp_path)

    # Assert
    # Check that the file exists and is a file.
    assert path.exists()
    assert path.is_file()

    content = json.loads(path.read_text())["data"]

    # Check that the dataset info is correct.
    assert content["name"] == "test_dataset"
    assert content["description"] == "A test dataset."
    assert content["uuid"] == str(dataset.uuid)

    # Check that the recording object is present.
    assert len(content["recordings"]) == 1

    # Check that the recording object contains all the required fields.
    assert content["recordings"][0]["uuid"] == str(dataset.recordings[0].uuid)
    assert content["recordings"][0]["path"] == "audio.wav"
    assert content["recordings"][0]["duration"] == 10.0
    assert content["recordings"][0]["channels"] == 1
    assert content["recordings"][0]["samplerate"] == 44100

    # Check that the recording object does not contain any optional fields.
    assert "time_expansion" not in content["recordings"][0]
    assert "hash" not in content["recordings"][0]
    assert "date" not in content["recordings"][0]
    assert "time" not in content["recordings"][0]
    assert "latitude" not in content["recordings"][0]
    assert "longitude" not in content["recordings"][0]
    assert "tags" not in content["recordings"][0]
    assert "features" not in content["recordings"][0]
    assert "notes" not in content["recordings"][0]


def test_save_dataset_with_one_recording_with_full_metadata(
    tmp_path: Path,
):
    """Test saving a dataset with one recording to the AOEF format."""
    # Arrange
    path = tmp_path / "dataset.json"
    dataset = data.Dataset(
        name="test_dataset",
        description="A test dataset.",
        recordings=[
            data.Recording(
                path=tmp_path / "audio.wav",
                duration=10.0,
                channels=1,
                samplerate=44100,
                time_expansion=10.0,
                hash="1234567890abcdef",
                date=datetime.date(2021, 1, 1),
                time=datetime.time(12, 34, 56),
                latitude=12.345,
                longitude=34.567,
            )
        ],
    )

    # Act
    io.save(dataset, path, audio_dir=tmp_path)

    # Assert
    assert path.exists()
    assert path.is_file()
    content = json.loads(path.read_text())["data"]
    assert content["name"] == "test_dataset"
    assert content["description"] == "A test dataset."
    assert content["uuid"] == str(dataset.uuid)
    assert len(content["recordings"]) == 1
    assert content["recordings"][0]["uuid"] == str(dataset.recordings[0].uuid)
    assert content["recordings"][0]["path"] == "audio.wav"
    assert content["recordings"][0]["duration"] == 10.0
    assert content["recordings"][0]["channels"] == 1
    assert content["recordings"][0]["samplerate"] == 44100
    assert content["recordings"][0]["time_expansion"] == 10.0
    assert content["recordings"][0]["hash"] == "1234567890abcdef"
    assert content["recordings"][0]["date"] == "2021-01-01"
    assert content["recordings"][0]["time"] == "12:34:56"
    assert content["recordings"][0]["latitude"] == 12.345
    assert content["recordings"][0]["longitude"] == 34.567


def test_save_dataset_with_one_recording_with_tags(
    tmp_path: Path,
):
    """Test saving a dataset with one recording to the AOEF format."""
    # Arrange
    path = tmp_path / "dataset.json"
    dataset = data.Dataset(
        name="test_dataset",
        description="A test dataset.",
        recordings=[
            data.Recording(
                path=tmp_path / "audio.wav",
                duration=10.0,
                channels=1,
                samplerate=44100,
                tags=[
                    data.Tag(
                        key="species",
                        value="Myotis myotis",
                    ),
                    data.Tag(
                        key="sex",
                        value="female",
                    ),
                    data.Tag(
                        key="behaviour",
                        value="foraging",
                    ),
                ],
            )
        ],
    )

    # Act
    io.save(dataset, path, audio_dir=tmp_path)

    # Assert
    assert path.exists()
    assert path.is_file()
    content = json.loads(path.read_text())["data"]

    assert len(content["recordings"]) == 1
    assert content["recordings"][0]["tags"] == [0, 1, 2]

    assert len(content["tags"]) == 3
    assert content["tags"][0]["key"] == "species"
    assert content["tags"][0]["value"] == "Myotis myotis"
    assert content["tags"][1]["key"] == "sex"
    assert content["tags"][1]["value"] == "female"
    assert content["tags"][2]["key"] == "behaviour"
    assert content["tags"][2]["value"] == "foraging"


def test_save_dataset_with_one_recording_with_features(
    tmp_path: Path,
):
    """Test saving a dataset with one recording to the AOEF format."""
    # Arrange
    path = tmp_path / "dataset.json"
    dataset = data.Dataset(
        name="test_dataset",
        description="A test dataset.",
        recordings=[
            data.Recording(
                path=tmp_path / "audio.wav",
                duration=10.0,
                channels=1,
                samplerate=44100,
                features=[
                    data.Feature(
                        name="SNR",
                        value=10.0,
                    ),
                    data.Feature(
                        name="ACI",
                        value=0.5,
                    ),
                    data.Feature(
                        name="ADI",
                        value=2.0,
                    ),
                ],
            )
        ],
    )

    # Act
    io.save(dataset, path, audio_dir=tmp_path)

    # Assert
    assert path.exists()
    assert path.is_file()
    content = json.loads(path.read_text())["data"]

    assert len(content["recordings"]) == 1
    assert content["recordings"][0]["features"] == {
        "SNR": 10.0,
        "ACI": 0.5,
        "ADI": 2.0,
    }


def test_save_and_load_dataset_recover_the_same_object(
    tmp_path: Path,
):
    """Check that saving and loading a dataset does not change the object."""
    # Arrange
    path = tmp_path / "dataset.json"

    dataset = data.Dataset(
        name="test_dataset",
        description="A test dataset.",
        recordings=[
            data.Recording(
                path=tmp_path / "audio.wav",
                duration=10.0,
                channels=1,
                samplerate=44100,
                time_expansion=10.0,
                hash="1234567890abcdef",
                date=datetime.date(2021, 1, 1),
                time=datetime.time(12, 34, 56),
                latitude=12.345,
                longitude=34.567,
                tags=[
                    data.Tag(
                        key="species",
                        value="Myotis myotis",
                    ),
                    data.Tag(
                        key="sex",
                        value="female",
                    ),
                    data.Tag(
                        key="behaviour",
                        value="foraging",
                    ),
                ],
                features=[
                    data.Feature(
                        name="SNR",
                        value=10.0,
                    ),
                    data.Feature(
                        name="ACI",
                        value=0.5,
                    ),
                ],
                notes=[
                    data.Note(
                        message="This is a note.",
                        created_by=data.User(name="John Doe"),
                        created_on=datetime.datetime(2021, 1, 1, 12, 34, 56),
                    ),
                ],
            )
        ],
    )

    # Act
    io.save(dataset, path, audio_dir=tmp_path)
    loaded_dataset = io.load(path, audio_dir=tmp_path)

    # Assert
    assert loaded_dataset == dataset
