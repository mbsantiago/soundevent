"""Test suite for annotation project saving functions."""

import datetime
import json
from pathlib import Path

from soundevent import data, io

BASE_DIR = Path(__file__).parent.parent.parent


def test_annotation_project_is_recovered(
    annotation_project: data.AnnotationProject,
    audio_dir: Path,
):
    """Test that the annotation project is recovered."""
    # Arrange
    path = audio_dir / "test_project.json"

    # Act
    io.save(annotation_project, path, audio_dir=audio_dir)
    recovered = io.load(path, audio_dir=audio_dir)

    # Assert
    assert recovered == annotation_project


def test_saved_annotation_project_is_saved_to_json_file(
    tmp_path: Path,
):
    """Test that the annotation project is saved to a JSON file."""
    # Arrange
    annotation_project = data.AnnotationProject(name="test_project")
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)

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
    io.save(annotation_project, path)

    # Assert
    doc = json.loads(path.read_text("utf-8"))
    assert doc["created_on"] == "2023-07-16T00:00:00"

    recovered = doc["data"]
    assert recovered["uuid"] == str(annotation_project.uuid)
    assert recovered["name"] == "test_project"
    assert recovered["description"] == "test_description"
    assert recovered["instructions"] == "test_instructions"


def test_can_recover_empty_project(
    tmp_path: Path,
):
    """Test that an empty annotation project can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(name="test_project")
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)
    recovered = io.load(path)

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
        clip_annotations=[data.ClipAnnotation(clip=clip)],
        tasks=[data.AnnotationTask(clip=clip)],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path, audio_dir=tmp_path)
    recovered = io.load(path, audio_dir=tmp_path)

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
        clip_annotations=[
            data.ClipAnnotation(
                clip=clip,
                tags=[
                    data.Tag(
                        term=data.term_from_key("species"),
                        value="Myotis lucifugus",
                    ),
                ],
            )
        ],
        tasks=[
            data.AnnotationTask(
                clip=clip,
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)
    recovered = io.load(path, type="annotation_project")

    # Assert
    assert recovered == annotation_project
    assert recovered.clip_annotations[0].tags[0].term == data.term_from_key(
        "species"
    )
    assert recovered.clip_annotations[0].tags[0].value == "Myotis lucifugus"


def test_can_recover_task_status(
    tmp_path: Path,
    clip: data.Clip,
):
    """Test that task status can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                status_badges=[
                    data.StatusBadge(
                        state=data.AnnotationState.completed,
                    )
                ],
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)
    recovered = io.load(path, type="annotation_project")

    # Assert
    assert recovered == annotation_project
    assert (
        recovered.tasks[0].status_badges[0].state
        == data.AnnotationState.completed
    )


def test_can_recover_user_that_completed_task(
    tmp_path: Path, clip: data.Clip, user: data.User
):
    """Test that the user that completed a task can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                status_badges=[
                    data.StatusBadge(
                        state=data.AnnotationState.completed,
                        owner=user,
                    )
                ],
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)
    recovered = io.load(path, type="annotation_project")

    # Assert
    assert recovered.model_dump() == annotation_project.model_dump()
    badge = recovered.tasks[0].status_badges[0]
    assert badge.state == data.AnnotationState.completed
    assert badge.owner == user


def test_can_recover_task_notes(
    tmp_path: Path,
    clip: data.Clip,
    user: data.User,
):
    """Test that task notes can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        clip_annotations=[
            data.ClipAnnotation(
                clip=clip,
                notes=[data.Note(message="test note", created_by=user)],
            )
        ],
        tasks=[data.AnnotationTask(clip=clip)],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)
    recovered = io.load(path, type="annotation_project")

    # Assert
    assert recovered == annotation_project
    assert recovered.clip_annotations[0].notes[0].message == "test note"
    assert recovered.clip_annotations[0].notes[0].created_by == user


def test_can_recover_task_completion_date(tmp_path: Path, clip: data.Clip):
    """Test that task completion date can be recovered."""
    # Arrange
    date = datetime.datetime(2021, 1, 1, 0, 0, 0)
    annotation_project = data.AnnotationProject(
        name="test_project",
        tasks=[
            data.AnnotationTask(
                clip=clip,
                status_badges=[
                    data.StatusBadge(
                        state=data.AnnotationState.completed,
                        created_on=date,
                    )
                ],
            )
        ],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)
    recovered = io.load(path, type="annotation_project")

    # Assert
    assert recovered == annotation_project
    badge = recovered.tasks[0].status_badges[0]
    assert badge.state == data.AnnotationState.completed
    assert badge.created_on == date


def test_can_recover_task_simple_annotation(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
):
    """Test that simple annotations can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        clip_annotations=[
            data.ClipAnnotation(
                clip=clip,
                sound_events=[
                    data.SoundEventAnnotation(sound_event=sound_event)
                ],
            )
        ],
        tasks=[data.AnnotationTask(clip=clip)],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)
    recovered = io.load(path, type="annotation_project")

    # Assert
    assert recovered == annotation_project
    assert (
        recovered.clip_annotations[0].sound_events[0].sound_event.geometry
        is not None
    )
    assert sound_event.geometry is not None
    assert (
        recovered.clip_annotations[0].sound_events[0].sound_event.geometry.type
        == sound_event.geometry.type
    )
    assert (
        recovered.clip_annotations[0]
        .sound_events[0]
        .sound_event.geometry.coordinates
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
        clip_annotations=[
            data.ClipAnnotation(
                clip=clip,
                sound_events=[
                    data.SoundEventAnnotation(
                        sound_event=sound_event,
                        tags=[
                            data.Tag(
                                term=data.term_from_key("species"),
                                value="test_species",
                            )
                        ],
                    )
                ],
            )
        ],
        tasks=[data.AnnotationTask(clip=clip)],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)
    recovered = io.load(path, type="annotation_project")

    # Assert
    assert recovered == annotation_project
    assert recovered.clip_annotations[0].sound_events[0].tags[
        0
    ].term == data.term_from_key("species")
    assert (
        recovered.clip_annotations[0].sound_events[0].tags[0].value
        == "test_species"
    )


def test_can_recover_annotation_creator(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
    user: data.User,
):
    """Test that annotation creator can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        clip_annotations=[
            data.ClipAnnotation(
                clip=clip,
                sound_events=[
                    data.SoundEventAnnotation(
                        sound_event=sound_event,
                        created_by=user,
                    )
                ],
            )
        ],
        tasks=[data.AnnotationTask(clip=clip)],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)
    recovered = io.load(path, type="annotation_project")

    # Assert
    assert recovered == annotation_project
    assert recovered.clip_annotations[0].sound_events[0].created_by == user


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
        clip_annotations=[
            data.ClipAnnotation(
                clip=clip,
                sound_events=[
                    data.SoundEventAnnotation(
                        sound_event=sound_event, created_on=date
                    )
                ],
            ),
        ],
        tasks=[data.AnnotationTask(clip=clip)],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)
    recovered = io.load(path, type="annotation_project")

    # Assert
    assert recovered == annotation_project
    assert recovered.clip_annotations[0].sound_events[0].created_on == date


def test_can_recover_annotation_notes(
    tmp_path: Path,
    clip: data.Clip,
    sound_event: data.SoundEvent,
    user: data.User,
):
    """Test that annotation notes can be recovered."""
    # Arrange
    annotation_project = data.AnnotationProject(
        name="test_project",
        clip_annotations=[
            data.ClipAnnotation(
                clip=clip,
                sound_events=[
                    data.SoundEventAnnotation(
                        sound_event=sound_event,
                        notes=[
                            data.Note(
                                message="test_note",
                                created_by=user,
                            )
                        ],
                    )
                ],
            )
        ],
        tasks=[data.AnnotationTask(clip=clip)],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)
    recovered = io.load(path, type="annotation_project")

    # Assert
    assert recovered == annotation_project
    assert (
        recovered.clip_annotations[0].sound_events[0].notes[0].message
        == "test_note"
    )
    assert (
        recovered.clip_annotations[0].sound_events[0].notes[0].created_by
        == user
    )


def test_can_recover_sound_event_features(
    tmp_path: Path,
    clip: data.Clip,
    bounding_box: data.BoundingBox,
):
    """Test that sound event features can be recovered."""
    # Arrange
    term = data.term_from_key("duration")
    annotation_project = data.AnnotationProject(
        name="test_project",
        clip_annotations=[
            data.ClipAnnotation(
                clip=clip,
                sound_events=[
                    data.SoundEventAnnotation(
                        sound_event=data.SoundEvent(
                            recording=clip.recording,
                            geometry=bounding_box,
                            features=[
                                data.Feature(term=term, value=1.0),
                            ],
                        )
                    )
                ],
            )
        ],
        tasks=[data.AnnotationTask(clip=clip)],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path)
    recovered = io.load(path, type="annotation_project")

    # Assert
    assert recovered.model_dump() == annotation_project.model_dump()
    assert (
        recovered.clip_annotations[0]
        .sound_events[0]
        .sound_event.features[0]
        .term.label
        == "duration"
    )
    assert (
        recovered.clip_annotations[0]
        .sound_events[0]
        .sound_event.features[0]
        .value
        == 1.0
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
        clip_annotations=[data.ClipAnnotation(clip=clip)],
        tasks=[data.AnnotationTask(clip=clip)],
    )
    path = tmp_path / "test_project.json"

    # Act
    io.save(annotation_project, path, audio_dir=audio_dir)

    # Assert
    recovered = json.loads(path.read_text("utf-8"))["data"]

    assert recovered["recordings"][0]["path"] == "test.wav"


def test_can_parse_nips4plus(tmp_path: Path):
    """Test that NIPS4BPlus annotations can be parsed."""
    original_path = (
        BASE_DIR / "docs" / "user_guide" / "nips4b_plus_sample.json"
    )
    path = tmp_path / "test.json"

    # Act
    annotation_project = io.load(original_path)
    io.save(annotation_project, tmp_path / "test.json")
    recovered = io.load(path)

    # Assert
    assert recovered == annotation_project
