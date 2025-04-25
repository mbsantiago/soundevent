from uuid import uuid4

import pytest

from soundevent import data
from soundevent.operations.tags import TagTransform

new_tag = data.Tag(
    term=data.Term(name="new", label="New", definition="test"),
    value="added",
)


def append_tag_transform(tags: list[data.Tag]) -> list[data.Tag]:
    return tags + [new_tag]


def remove_all_tags_transform(tags: list[data.Tag]) -> list[data.Tag]:
    return []


def test_tag_transform_init():
    """Test TagTransform initialization."""
    transformer = TagTransform(tag_transform=append_tag_transform)
    assert transformer.tag_transform == append_tag_transform


def test_transform_tags(random_tags):
    """Test the core transform_tags method."""
    initial_tags = random_tags(3)
    transformer = TagTransform(tag_transform=append_tag_transform)
    transformed_tags = transformer.transform_tags(initial_tags)
    assert transformed_tags == initial_tags + [new_tag]
    assert len(initial_tags) == 3


def test_transform_recording(recording, random_tags):
    """Test transforming tags in a Recording."""
    initial_tags = random_tags(2)
    recording_with_tags = recording.model_copy(update=dict(tags=initial_tags))
    transformer = TagTransform(tag_transform=append_tag_transform)

    transformed_recording = transformer.transform_recording(
        recording_with_tags
    )

    assert isinstance(transformed_recording, data.Recording)
    assert transformed_recording is not recording_with_tags
    assert transformed_recording.tags == initial_tags + [new_tag]
    assert recording_with_tags.tags == initial_tags
    assert transformed_recording.uuid == recording_with_tags.uuid
    assert transformed_recording.path == recording_with_tags.path


def test_transform_sound_event(sound_event, random_tags):
    """Test transforming tags in a SoundEvent's Recording."""
    initial_rec_tags = random_tags(1)
    recording_with_tags = sound_event.recording.model_copy(
        update=dict(tags=initial_rec_tags)
    )
    sound_event_with_tags = sound_event.model_copy(
        update=dict(recording=recording_with_tags)
    )
    transformer = TagTransform(tag_transform=append_tag_transform)

    transformed_sound_event = transformer.transform_sound_event(
        sound_event_with_tags
    )

    assert isinstance(transformed_sound_event, data.SoundEvent)
    assert transformed_sound_event is not sound_event_with_tags
    assert transformed_sound_event.recording.tags == initial_rec_tags + [
        new_tag
    ]
    assert sound_event_with_tags.recording.tags == initial_rec_tags
    assert transformed_sound_event.uuid == sound_event_with_tags.uuid
    assert (
        transformed_sound_event.recording.uuid
        == sound_event_with_tags.recording.uuid
    )


def test_transform_sound_event_annotation(sound_event_annotation, random_tags):
    """Test transforming tags in a SoundEventAnnotation."""
    initial_annot_tags = random_tags(3)
    initial_rec_tags = random_tags(1)

    recording_with_tags = (
        sound_event_annotation.sound_event.recording.model_copy(
            update=dict(tags=initial_rec_tags)
        )
    )
    sound_event_with_tags = sound_event_annotation.sound_event.model_copy(
        update=dict(recording=recording_with_tags)
    )
    annotation_with_tags = sound_event_annotation.model_copy(
        update=dict(tags=initial_annot_tags, sound_event=sound_event_with_tags)
    )

    transformer = TagTransform(tag_transform=append_tag_transform)
    transformed_annotation = transformer.transform_sound_event_annotation(
        annotation_with_tags
    )

    assert isinstance(transformed_annotation, data.SoundEventAnnotation)
    assert transformed_annotation is not annotation_with_tags
    assert transformed_annotation.tags == initial_annot_tags + [new_tag]
    assert (
        transformed_annotation.sound_event.recording.tags
        == initial_rec_tags + [new_tag]
    )
    assert annotation_with_tags.tags == initial_annot_tags
    assert annotation_with_tags.sound_event.recording.tags == initial_rec_tags
    assert transformed_annotation.uuid == annotation_with_tags.uuid
    assert (
        transformed_annotation.sound_event.uuid
        == annotation_with_tags.sound_event.uuid
    )


def test_transform_clip(clip, random_tags):
    """Test transforming tags in a Clip's Recording."""
    initial_rec_tags = random_tags(4)
    recording_with_tags = clip.recording.model_copy(
        update=dict(tags=initial_rec_tags)
    )
    clip_with_tags = clip.model_copy(
        update=dict(recording=recording_with_tags)
    )
    transformer = TagTransform(tag_transform=append_tag_transform)

    transformed_clip = transformer.transform_clip(clip_with_tags)

    assert isinstance(transformed_clip, data.Clip)
    assert transformed_clip is not clip_with_tags
    assert transformed_clip.recording.tags == initial_rec_tags + [new_tag]
    assert clip_with_tags.recording.tags == initial_rec_tags
    assert transformed_clip.uuid == clip_with_tags.uuid
    assert transformed_clip.recording.uuid == clip_with_tags.recording.uuid


@pytest.fixture
def clip_annotation(
    clip: data.Clip,
    sound_event_annotation: data.SoundEventAnnotation,
    random_tags,
) -> data.ClipAnnotation:
    """Create a ClipAnnotation fixture."""
    rec_tags = random_tags(1)
    clip_rec = clip.recording.model_copy(update=dict(tags=rec_tags))
    test_clip = clip.model_copy(update=dict(recording=clip_rec))

    se_rec_tags = random_tags(1)
    se_annot_tags = random_tags(1)
    se_rec = sound_event_annotation.sound_event.recording.model_copy(
        update=dict(tags=se_rec_tags)
    )
    test_se = sound_event_annotation.sound_event.model_copy(
        update=dict(recording=se_rec)
    )
    test_se_annot = sound_event_annotation.model_copy(
        update=dict(tags=se_annot_tags, sound_event=test_se)
    )

    return data.ClipAnnotation(
        clip=test_clip,
        tags=random_tags(2),
        sound_events=[test_se_annot],
    )


@pytest.fixture
def annotation_task(clip: data.Clip, random_tags) -> data.AnnotationTask:
    """Create an AnnotationTask fixture."""
    rec_tags = random_tags(1)
    recording_with_tags = clip.recording.model_copy(update=dict(tags=rec_tags))
    clip_with_tags = clip.model_copy(
        update=dict(recording=recording_with_tags)
    )
    return data.AnnotationTask(clip=clip_with_tags)


@pytest.fixture
def dataset(recording: data.Recording, random_tags) -> data.Dataset:
    """Create a Dataset fixture."""
    recordings = [
        recording.model_copy(update=dict(uuid=uuid4(), tags=random_tags(i)))
        for i in range(1, 3)
    ]
    return data.Dataset(name="tests", recordings=recordings)


@pytest.fixture
def annotation_project(
    clip_annotation: data.ClipAnnotation,
    annotation_task: data.AnnotationTask,
) -> data.AnnotationProject:
    """Create an AnnotationProject fixture."""
    ca = clip_annotation.model_copy(deep=True)
    at = annotation_task.model_copy(deep=True)
    return data.AnnotationProject(clip_annotations=[ca], tasks=[at])


def test_transform_clip_annotation(clip_annotation, random_tags):
    """Test transforming tags in a ClipAnnotation."""
    initial_clip_annot_tags = clip_annotation.tags
    initial_clip_rec_tags = clip_annotation.clip.recording.tags
    initial_se_annot_tags = clip_annotation.sound_events[0].tags
    initial_se_rec_tags = clip_annotation.sound_events[
        0
    ].sound_event.recording.tags

    transformer = TagTransform(tag_transform=append_tag_transform)
    transformed_clip_annot = transformer.transform_clip_annotation(
        clip_annotation
    )

    assert isinstance(transformed_clip_annot, data.ClipAnnotation)
    assert transformed_clip_annot is not clip_annotation

    assert transformed_clip_annot.tags == initial_clip_annot_tags + [new_tag]
    assert clip_annotation.tags == initial_clip_annot_tags

    assert (
        transformed_clip_annot.clip.recording.tags
        == initial_clip_rec_tags + [new_tag]
    )
    assert clip_annotation.clip.recording.tags == initial_clip_rec_tags

    assert transformed_clip_annot.sound_events[
        0
    ].tags == initial_se_annot_tags + [new_tag]
    assert clip_annotation.sound_events[0].tags == initial_se_annot_tags

    assert transformed_clip_annot.sound_events[
        0
    ].sound_event.recording.tags == initial_se_rec_tags + [new_tag]
    assert (
        clip_annotation.sound_events[0].sound_event.recording.tags
        == initial_se_rec_tags
    )

    assert transformed_clip_annot.uuid == clip_annotation.uuid
    assert transformed_clip_annot.clip.uuid == clip_annotation.clip.uuid
    assert (
        transformed_clip_annot.sound_events[0].uuid
        == clip_annotation.sound_events[0].uuid
    )


def test_transform_annotation_task(annotation_task):
    """Test transforming tags in an AnnotationTask."""
    initial_rec_tags = annotation_task.clip.recording.tags
    transformer = TagTransform(tag_transform=append_tag_transform)

    transformed_task = transformer.transform_annotation_task(annotation_task)

    assert isinstance(transformed_task, data.AnnotationTask)
    assert transformed_task is not annotation_task
    assert transformed_task.clip.recording.tags == initial_rec_tags + [new_tag]
    assert annotation_task.clip.recording.tags == initial_rec_tags
    assert transformed_task.uuid == annotation_task.uuid
    assert transformed_task.clip.uuid == annotation_task.clip.uuid


def test_transform_dataset(dataset):
    """Test transforming tags in a Dataset."""
    initial_rec_tags_list = [rec.tags for rec in dataset.recordings]
    transformer = TagTransform(tag_transform=append_tag_transform)

    transformed_dataset = transformer.transform_dataset(dataset)

    assert isinstance(transformed_dataset, data.Dataset)
    assert transformed_dataset is not dataset
    assert len(transformed_dataset.recordings) == len(dataset.recordings)

    for i, transformed_rec in enumerate(transformed_dataset.recordings):
        assert transformed_rec.tags == initial_rec_tags_list[i] + [new_tag]
        assert dataset.recordings[i].tags == initial_rec_tags_list[i]
        assert transformed_rec.uuid == dataset.recordings[i].uuid

    assert transformed_dataset.uuid == dataset.uuid


def test_transform_annotation_project(annotation_project):
    """Test transforming tags in an AnnotationProject."""
    initial_ca_tags = annotation_project.clip_annotations[0].tags
    initial_ca_clip_rec_tags = annotation_project.clip_annotations[
        0
    ].clip.recording.tags
    initial_ca_se_tags = (
        annotation_project.clip_annotations[0].sound_events[0].tags
    )
    initial_ca_se_rec_tags = (
        annotation_project.clip_annotations[0]
        .sound_events[0]
        .sound_event.recording.tags
    )
    initial_task_clip_rec_tags = annotation_project.tasks[
        0
    ].clip.recording.tags

    transformer = TagTransform(tag_transform=append_tag_transform)
    transformed_project = transformer.transform_annotation_project(
        annotation_project
    )

    assert isinstance(transformed_project, data.AnnotationProject)
    assert transformed_project is not annotation_project

    transformed_ca = transformed_project.clip_annotations[0]
    original_ca = annotation_project.clip_annotations[0]
    assert transformed_ca.tags == initial_ca_tags + [new_tag]
    assert original_ca.tags == initial_ca_tags
    assert transformed_ca.clip.recording.tags == initial_ca_clip_rec_tags + [
        new_tag
    ]
    assert original_ca.clip.recording.tags == initial_ca_clip_rec_tags
    assert transformed_ca.sound_events[0].tags == initial_ca_se_tags + [
        new_tag
    ]
    assert original_ca.sound_events[0].tags == initial_ca_se_tags
    assert transformed_ca.sound_events[
        0
    ].sound_event.recording.tags == initial_ca_se_rec_tags + [new_tag]
    assert (
        original_ca.sound_events[0].sound_event.recording.tags
        == initial_ca_se_rec_tags
    )

    transformed_task = transformed_project.tasks[0]
    original_task = annotation_project.tasks[0]
    assert (
        transformed_task.clip.recording.tags
        == initial_task_clip_rec_tags + [new_tag]
    )
    assert original_task.clip.recording.tags == initial_task_clip_rec_tags

    assert transformed_project.uuid == annotation_project.uuid
    assert (
        transformed_project.clip_annotations[0].uuid
        == annotation_project.clip_annotations[0].uuid
    )
    assert (
        transformed_project.tasks[0].uuid == annotation_project.tasks[0].uuid
    )


def test_transform_with_empty_tags(recording):
    """Test transformation when initial tags are empty."""
    recording_no_tags = recording.model_copy(update=dict(tags=[]))
    transformer = TagTransform(tag_transform=append_tag_transform)
    transformed_recording = transformer.transform_recording(recording_no_tags)
    assert transformed_recording.tags == [new_tag]
    assert recording_no_tags.tags == []


def test_transform_remove_all_tags(recording, random_tags):
    """Test transformation that removes all tags."""
    initial_tags = random_tags(3)
    recording_with_tags = recording.model_copy(update=dict(tags=initial_tags))
    transformer = TagTransform(tag_transform=remove_all_tags_transform)
    transformed_recording = transformer.transform_recording(
        recording_with_tags
    )
    assert transformed_recording.tags == []
    assert recording_with_tags.tags == initial_tags
