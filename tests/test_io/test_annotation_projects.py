"""Test suite for annotation project saving functions."""

import datetime
import json
from pathlib import Path

import pytest

from soundevent import data, io

BASE_DIR = Path(__file__).parent.parent.parent


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


def test_saved_annotation_project_is_saved_to_json_file(
    tmp_path: Path,
):
    """Test that the annotation project is saved to a JSON file."""
    # Arrange
    annotation_project = data.AnnotationProject(name="test_project")
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)

    # Assert
    assert path.exists()


def test_saved_annotation_project_has_correct_info(
    monkeypatch, tmp_path: Path
) -> None:
    """Test that the saved annotation project has the correct info."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        description="test_description",
        instructions="test_instructions",
    )
    now = datetime.datetime(2023, 7, 16, 0, 0, 0)

    class MockDateTime:
        @classmethod
        def now(cls):
            return now

    monkeypatch.setattr(datetime, "datetime", MockDateTime)
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)

    # Assert
    recovered = json.loads(path.read_text("utf-8"))
    assert recovered["info"]["uuid"] == str(annotation_project.id)
    assert recovered["info"]["name"] == "test_project"
    assert recovered["info"]["description"] == "test_description"
    assert recovered["info"]["instructions"] == "test_instructions"
    assert recovered["info"]["date_created"] == "2023-07-16T00:00:00"


def test_can_recover_empty_project(
    tmp_path: Path,
):
    """Test that an empty annotation project can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(name="test_project")
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project


def test_can_recover_project_with_empty_task(
    tmp_path: Path,
    clip: data.Clip,
):
    """Test that an annotation project with an empty task can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[data.AnnotationTask(clip=clip)],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project


def test_can_recover_tasks_with_predicted_tags(
    tmp_path: Path,
    clip: data.Clip,
):
    """Test that annotation projects with tasks and tags can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                tags=[
                    data.Tag(
                        key="species",
                        value="Myotis lucifugus",
                    ),
                ],
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
    assert recovered.tasks[0].tags[0].key == "species"
    assert recovered.tasks[0].tags[0].value == "Myotis lucifugus"


def test_can_recover_task_status(
    tmp_path: Path,
    clip: data.Clip,
):
    """Test that task status can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[data.AnnotationTask(clip=clip, completed=True)],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
    assert recovered.tasks[0].completed


def test_can_recover_user_that_completed_task(tmp_path: Path, clip: data.Clip):
    """Test that the user that completed a task can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                completed=True,
                completed_by="test_user",
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
    assert recovered.tasks[0].completed_by == "test_user"


def test_can_recover_task_notes(tmp_path: Path, clip: data.Clip):
    """Test that task notes can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                notes=[data.Note(message="test note", created_by="test_user")],
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
    assert recovered.tasks[0].notes[0].message == "test note"
    assert recovered.tasks[0].notes[0].created_by == "test_user"


def test_can_recover_task_completion_date(tmp_path: Path, clip: data.Clip):
    """Test that task completion date can be recovered."""
    # Arrange
    date = datetime.datetime(2021, 1, 1, 0, 0, 0)
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(clip=clip, completed=True, completed_on=date)
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
    assert recovered.tasks[0].completed_on == date


def test_can_recover_task_simple_annotation(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
    recording: data.Recording,
):
    """Test that simple annotations can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                annotations=[data.Annotation(sound_event=sound_event)],
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
    assert recovered.tasks[0].annotations[0].sound_event.recording == recording
    assert recovered.tasks[0].annotations[0].sound_event.geometry is not None
    assert sound_event.geometry is not None
    assert (
        recovered.tasks[0].annotations[0].sound_event.geometry.type
        == sound_event.geometry.type
    )
    assert (
        recovered.tasks[0].annotations[0].sound_event.geometry.coordinates
        == sound_event.geometry.coordinates
    )


def test_can_recover_task_annotation_with_tags(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
):
    """Test that annotations with tags can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                annotations=[
                    data.Annotation(
                        sound_event=sound_event,
                        tags=[
                            data.Tag(
                                key="species",
                                value="test_species",
                            )
                        ],
                    )
                ],
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
    assert recovered.tasks[0].annotations[0].tags[0].key == "species"
    assert recovered.tasks[0].annotations[0].tags[0].value == "test_species"


def test_can_recover_annotation_creator(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
):
    """Test that annotation creator can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                annotations=[
                    data.Annotation(
                        sound_event=sound_event, created_by="test_user"
                    )
                ],
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
    assert recovered.tasks[0].annotations[0].created_by == "test_user"


def test_can_recover_annotation_creation_date(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
):
    """Test that annotation creation date can be recovered."""
    # Arrange
    date = datetime.datetime(2021, 1, 1, 0, 0, 0)
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                annotations=[
                    data.Annotation(sound_event=sound_event, created_on=date)
                ],
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
    assert recovered.tasks[0].annotations[0].created_on == date


def test_can_recover_annotation_notes(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
):
    """Test that annotation notes can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                annotations=[
                    data.Annotation(
                        sound_event=sound_event,
                        notes=[
                            data.Note(
                                message="test_note", created_by="test_user"
                            )
                        ],
                    )
                ],
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
    assert recovered.tasks[0].annotations[0].notes[0].message == "test_note"
    assert recovered.tasks[0].annotations[0].notes[0].created_by == "test_user"


def test_can_recover_sound_event_tags(
    tmp_path: Path,
    clip: data.Clip,
    bounding_box: data.BoundingBox,
    recording: data.Recording,
):
    """Test that sound event tags can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                annotations=[
                    data.Annotation(
                        sound_event=data.SoundEvent(
                            recording=recording,
                            geometry=bounding_box,
                            tags=[
                                data.Tag(
                                    key="species",
                                    value="test_species",
                                ),
                            ],
                        )
                    )
                ],
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
    assert (
        recovered.tasks[0].annotations[0].sound_event.tags[0].key == "species"
    )
    assert (
        recovered.tasks[0].annotations[0].sound_event.tags[0].value
        == "test_species"
    )


def test_can_recover_sound_event_features(
    tmp_path: Path,
    clip: data.Clip,
    bounding_box: data.BoundingBox,
    recording: data.Recording,
):
    """Test that sound event features can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                annotations=[
                    data.Annotation(
                        sound_event=data.SoundEvent(
                            recording=recording,
                            geometry=bounding_box,
                            features=[
                                data.Feature(
                                    name="duration",
                                    value=1.0,
                                ),
                            ],
                        )
                    )
                ],
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path)
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
    assert (
        recovered.tasks[0].annotations[0].sound_event.features[0].name
        == "duration"
    )
    assert (
        recovered.tasks[0].annotations[0].sound_event.features[0].value == 1.0
    )


def test_recording_paths_are_stored_as_relative_if_audio_dir_is_provided(
    tmp_path: Path,
):
    """Test that recording paths are relative if audio dir is provided."""
    # Arrange
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    recording = data.Recording(
        path=audio_dir / "test.wav",
        duration=10,
        samplerate=44100,
        channels=1,
    )
    clip = data.Clip(
        recording=recording,
        start_time=0,
        end_time=5,
    )
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[data.AnnotationTask(clip=clip)],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save_annotation_project(annotation_project, path, audio_dir=audio_dir)

    # Assert
    recovered = json.loads(path.read_text("utf-8"))

    assert recovered["recordings"][0]["path"] == "test.wav"


def test_can_parse_nips4plus(tmp_path: Path):
    """Test that NIPS4BPlus annotations can be parsed."""
    original_path = (
        BASE_DIR / "docs" / "user_guide" / "nips4b_plus_sample.json"
    )
    path = tmp_path / "test.json"

    # Act
    annotation_project = io.load_annotation_project(original_path)
    io.save_annotation_project(annotation_project, tmp_path / "test.json")
    recovered = io.load_annotation_project(path)

    # Assert
    assert recovered == annotation_project
