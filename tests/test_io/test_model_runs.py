"""Test suite for ModelRun loading and saving functions."""

import datetime
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from soundevent import data, io


def test_model_run_is_recovered(
    model_run: data.ModelRun,
    audio_dir: Path,
) -> None:
    """Test that the model run is recovered."""
    # Arrange
    path = audio_dir / "model_run.json"

    # Act
    io.save(model_run, path, audio_dir=audio_dir)
    recovered = io.load(path, audio_dir=audio_dir)

    # Assert
    assert recovered == model_run


def test_saved_model_run_is_saved_to_json_file(
    tmp_path: Path,
) -> None:
    """Test that a saved model run is saved to a JSON file."""
    # Arrange
    model_run = data.ModelRun(
        name="test_model_run",
        description="test_description",
        model=data.Model(
            info=data.ModelInfo(name="test_model"),
            version="1.0.0",
        ),
    )
    path = tmp_path / "test.json"

    # Act
    io.save(model_run, path=path)

    # Assert
    assert path.exists()


def test_saved_model_run_has_correct_info(monkeypatch, tmp_path: Path) -> None:
    """Test that a saved model run has the correct info."""
    # Arrange
    model_run = data.ModelRun(
        name="test_model_run",
        description="test_description",
        model=data.Model(
            info=data.ModelInfo(name="test_model"),
            version="1.0.0",
        ),
    )
    now = datetime.datetime(2001, 7, 16, 0, 0, 0)

    class MockDateTime:
        @classmethod
        def now(cls):
            return now

    monkeypatch.setattr(datetime, "datetime", MockDateTime)
    path = tmp_path / "test_project.json"

    # Act
    io.save(model_run, path)

    # Assert
    recovered = json.loads(path.read_text("utf-8"))
    content = recovered["data"]
    assert content["uuid"] == str(model_run.uuid)
    assert content["name"] == model_run.name
    assert recovered["created_on"] == now.isoformat()


def test_can_recover_model_run_date(
    tmp_path: Path,
):
    """Test that a saved model run can be recovered."""
    # Arrange
    date = datetime.datetime(2001, 7, 16, 0, 0, 0)
    model_run = data.ModelRun(
        description="test_description",
        name="test_model_run",
        model=data.Model(
            info=data.ModelInfo(name="test_model"),
            version="1.0.0",
        ),
        created_on=date,
    )
    path = tmp_path / "test_project.json"
    io.save(model_run, path)

    # Act
    recovered = io.load(path)

    # Assert
    assert model_run == recovered
    assert recovered.created_on == date


def test_can_recover_simple_processed_clip(
    tmp_path: Path,
    clip: data.Clip,
) -> None:
    """Test that a saved model run can be recovered."""
    # Arrange
    model_run = data.ModelRun(
        description="test_description",
        name="test_model_run",
        model=data.Model(
            info=data.ModelInfo(name="test_model"),
            version="1.0.0",
        ),
        clip_predictions=[data.ClipPrediction(clip=clip)],
    )
    path = tmp_path / "test_project.json"
    io.save(model_run, path)

    # Act
    recovered = io.load(path)

    # Assert
    assert model_run == recovered


def test_can_recover_processed_clip_tags(
    tmp_path: Path,
    clip: data.Clip,
) -> None:
    """Test that a saved model run can be recovered."""
    # Arrange
    model_run = data.ModelRun(
        description="test_description",
        name="test_model_run",
        model=data.Model(
            info=data.ModelInfo(name="test_model"),
            version="1.0.0",
        ),
        clip_predictions=[
            data.ClipPrediction(
                clip=clip,
                tags=[
                    data.PredictedTag(
                        tag=data.Tag(
                            key="species",
                            value="Myotis lucifugus",
                        ),
                        score=0.9,
                    ),
                ],
            )
        ],
    )
    path = tmp_path / "test_project.json"
    io.save(model_run, path)

    # Act
    recovered = io.load(path, type="model_run")

    # Assert
    assert model_run == recovered
    assert recovered.clip_predictions[0].tags[0].tag.key == "species"
    assert (
        recovered.clip_predictions[0].tags[0].tag.value == "Myotis lucifugus"
    )
    assert recovered.clip_predictions[0].tags[0].score == 0.9


def test_can_recover_processed_clip_features(
    tmp_path: Path,
    clip: data.Clip,
) -> None:
    """Test that a saved model run can be recovered."""
    # Arrange
    model_run = data.ModelRun(
        description="test_description",
        name="test_model_run",
        model=data.Model(
            info=data.ModelInfo(name="test_model"),
            version="1.0.0",
        ),
        clip_predictions=[
            data.ClipPrediction(
                clip=clip,
                features=[
                    data.Feature(
                        name="SNR",
                        value=6,
                    ),
                ],
            )
        ],
    )
    path = tmp_path / "test_project.json"
    io.save(model_run, path)

    # Act
    recovered = io.load(path, type="model_run")

    # Assert
    assert model_run.model_dump(
        exclude_none=True,
        exclude_defaults=True,
    ) == recovered.model_dump(
        exclude_none=True,
        exclude_defaults=True,
    )
    assert recovered.clip_predictions[0].features[0].name == "SNR"
    assert recovered.clip_predictions[0].features[0].value == 6


def test_can_recover_simple_predicted_sound_event(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
) -> None:
    """Test that a saved model run can be recovered."""
    # Arrange
    model_run = data.ModelRun(
        description="test_description",
        name="test_model_run",
        model=data.Model(
            info=data.ModelInfo(name="test_model"),
            version="1.0.0",
        ),
        clip_predictions=[
            data.ClipPrediction(
                clip=clip,
                sound_events=[
                    data.SoundEventPrediction(
                        sound_event=sound_event,
                        score=0.9,
                    )
                ],
            ),
        ],
    )
    path = tmp_path / "test_project.json"
    io.save(model_run, path)

    # Act
    recovered = io.load(path, type="model_run")

    # Assert
    assert recovered.clip_predictions[0].sound_events[0].score == 0.9
    assert (
        recovered.clip_predictions[0].sound_events[0].sound_event
        == sound_event
    )
    assert model_run == recovered


def test_can_recover_predicted_sound_event_with_predicted_tags(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
) -> None:
    """Test that a saved model run can be recovered."""
    # Arrange
    model_run = data.ModelRun(
        description="test_description",
        name="test_model_run",
        model=data.Model(
            info=data.ModelInfo(name="test_model"),
            version="1.0.0",
        ),
        clip_predictions=[
            data.ClipPrediction(
                clip=clip,
                sound_events=[
                    data.SoundEventPrediction(
                        sound_event=sound_event,
                        tags=[
                            data.PredictedTag(
                                tag=data.Tag(
                                    key="species",
                                    value="Myotis lucifugus",
                                ),
                                score=0.9,
                            ),
                        ],
                    )
                ],
            ),
        ],
    )
    path = tmp_path / "test_project.json"
    io.save(model_run, path)

    # Act
    recovered = io.load(path, type="model_run")

    # Assert
    assert (
        recovered.clip_predictions[0].sound_events[0].tags[0].tag.key
        == "species"
    )
    assert (
        recovered.clip_predictions[0].sound_events[0].tags[0].tag.value
        == "Myotis lucifugus"
    )
    assert recovered.clip_predictions[0].sound_events[0].tags[0].score == 0.9
    assert model_run == recovered


def test_model_run_version_field_is_deprecated():
    """Test that the version field is deprecated."""
    # Act
    with pytest.deprecated_call():
        model_run = data.ModelRun(  # type: ignore
            description="test_description",
            name="test_model_run",
            version="1.0.0",  # type: ignore
        )

    # Assert
    assert model_run.model.version == "1.0.0"


def test_changing_model_run_version_is_deprecated():
    """Test that changing the version field is deprecated."""
    # Arrange
    model_run = data.ModelRun(
        description="test_description",
        name="test_model_run",
        model=data.Model(
            info=data.ModelInfo(name="test_model"),
            version="1.0.0",
        ),
    )

    # Act
    with pytest.deprecated_call():
        model_run.version = "2.0.0"  # type: ignore

    # Assert
    assert model_run.model.version == "2.0.0"


def test_can_create_model_run_with_version():
    """Test that a model run can be created with a version."""
    # Arrange
    model_run = data.ModelRun.model_validate(
        {
            "description": "test_description",
            "name": "test_model_run",
            "version": "1.0.0",
        }
    )

    # Assert
    assert model_run.model.version == "1.0.0"


def test_create_model_run_without_version_will_fail():
    """Test that a model run cannot be created without a version."""
    # Act
    with pytest.raises(ValidationError):
        data.ModelRun.model_validate(
            {
                "description": "test_description",
                "name": "test_model_run",
            }
        )
