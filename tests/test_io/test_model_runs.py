"""Test suite for ModelRun loading and saving functions."""

import datetime
import json
from pathlib import Path

import pytest

from soundevent import data, io


@pytest.fixture
def recording(tmp_path: Path) -> data.Recording:
    """Return a recording."""
    return data.Recording(
        path=tmp_path / "test.wav",
        duration=10.0,
        samplerate=44100,
        channels=1,
    )


@pytest.fixture
def clip(recording: data.Recording) -> data.Clip:
    """Return a clip."""
    return data.Clip(
        recording=recording,
        start_time=0.0,
        end_time=10.0,
    )


@pytest.fixture
def bounding_box() -> data.BoundingBox:
    """Return a bounding box."""
    return data.BoundingBox(coordinates=[0.0, 0.0, 1.0, 1.0])


@pytest.fixture
def sound_event(
    recording: data.Recording,
    bounding_box: data.BoundingBox,
) -> data.SoundEvent:
    """Return a sound event."""
    return data.SoundEvent(
        recording=recording,
        geometry=bounding_box,
    )


def test_saved_model_run_is_saved_to_json_file(
    tmp_path: Path,
) -> None:
    """Test that a saved model run is saved to a JSON file."""
    # Arrange
    model_run = data.ModelRun(model="test_model")
    path = tmp_path / "test.json"

    # Act
    io.save_model_run(model_run=model_run, path=path)

    # Assert
    assert path.exists()


def test_saved_model_run_has_correct_info(monkeypatch, tmp_path: Path) -> None:
    """Test that a saved model run has the correct info."""
    # Arrange
    model_run = data.ModelRun(
        model="test_model",
    )
    now = datetime.datetime(2001, 7, 16, 0, 0, 0)

    class MockDateTime:
        @classmethod
        def now(cls):
            return now

    monkeypatch.setattr(datetime, "datetime", MockDateTime)
    path = tmp_path / "test_project.json"

    # Act
    io.save_model_run(model_run, path)

    # Assert
    recovered = json.loads(path.read_text("utf-8"))
    assert recovered["info"]["uuid"] == str(model_run.id)
    assert recovered["info"]["model"] == model_run.model
    assert recovered["info"]["date_created"] == now.isoformat()


def test_can_recover_model_run_date(
    tmp_path: Path,
):
    """Test that a saved model run can be recovered."""
    # Arrange
    date = datetime.datetime(2001, 7, 16, 0, 0, 0)
    model_run = data.ModelRun(
        model="test_model",
        created_on=date,
    )
    path = tmp_path / "test_project.json"
    io.save_model_run(model_run, path)

    # Act
    recovered = io.load_model_run(path)

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
        model="test_model",
        clips=[data.ProcessedClip(clip=clip)],
    )
    path = tmp_path / "test_project.json"
    io.save_model_run(model_run, path)

    # Act
    recovered = io.load_model_run(path)

    # Assert
    assert model_run == recovered


def test_can_recover_processed_clip_tags(
    tmp_path: Path,
    clip: data.Clip,
) -> None:
    """Test that a saved model run can be recovered."""
    # Arrange
    model_run = data.ModelRun(
        model="test_model",
        clips=[
            data.ProcessedClip(
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
    io.save_model_run(model_run, path)

    # Act
    recovered = io.load_model_run(path)

    # Assert
    assert model_run == recovered
    assert recovered.clips[0].tags[0].tag.key == "species"
    assert recovered.clips[0].tags[0].tag.value == "Myotis lucifugus"
    assert recovered.clips[0].tags[0].score == 0.9


def test_can_recover_processed_clip_features(
    tmp_path: Path,
    clip: data.Clip,
) -> None:
    """Test that a saved model run can be recovered."""
    # Arrange
    model_run = data.ModelRun(
        model="test_model",
        clips=[
            data.ProcessedClip(
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
    io.save_model_run(model_run, path)

    # Act
    recovered = io.load_model_run(path)

    # Assert
    assert model_run == recovered
    assert recovered.clips[0].features[0].name == "SNR"
    assert recovered.clips[0].features[0].value == 6


def test_can_recover_simple_predicted_sound_event(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
) -> None:
    """Test that a saved model run can be recovered."""
    # Arrange
    model_run = data.ModelRun(
        model="test_model",
        clips=[
            data.ProcessedClip(
                clip=clip,
                sound_events=[
                    data.PredictedSoundEvent(
                        sound_event=sound_event,
                        score=0.9,
                    )
                ],
            ),
        ],
    )
    path = tmp_path / "test_project.json"
    io.save_model_run(model_run, path)

    # Act
    recovered = io.load_model_run(path)

    # Assert
    assert recovered.clips[0].sound_events[0].score == 0.9
    assert recovered.clips[0].sound_events[0].sound_event == sound_event
    assert model_run == recovered


def test_can_recover_predicted_sound_event_with_predicted_tags(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
) -> None:
    """Test that a saved model run can be recovered."""
    # Arrange
    model_run = data.ModelRun(
        model="test_model",
        clips=[
            data.ProcessedClip(
                clip=clip,
                sound_events=[
                    data.PredictedSoundEvent(
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
    io.save_model_run(model_run, path)

    # Act
    recovered = io.load_model_run(path)

    # Assert
    assert recovered.clips[0].sound_events[0].tags[0].tag.key == "species"
    assert (
        recovered.clips[0].sound_events[0].tags[0].tag.value
        == "Myotis lucifugus"
    )
    assert recovered.clips[0].sound_events[0].tags[0].score == 0.9
    assert model_run == recovered


def test_can_recover_predicted_sound_event_with_predicted_features(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
) -> None:
    """Test that a saved model run can be recovered."""
    # Arrange
    model_run = data.ModelRun(
        model="test_model",
        clips=[
            data.ProcessedClip(
                clip=clip,
                sound_events=[
                    data.PredictedSoundEvent(
                        sound_event=sound_event,
                        features=[
                            data.Feature(
                                name="SNR",
                                value=6,
                            ),
                        ],
                    )
                ],
            ),
        ],
    )
    path = tmp_path / "test_project.json"
    io.save_model_run(model_run, path)

    # Act
    recovered = io.load_model_run(path)

    # Assert
    assert recovered.clips[0].sound_events[0].features[0].name == "SNR"
    assert recovered.clips[0].sound_events[0].features[0].value == 6
    assert model_run == recovered
