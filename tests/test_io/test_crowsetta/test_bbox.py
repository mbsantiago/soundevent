"""Test suite for the soundevent.io.crowsetta.bbox module."""

import crowsetta
import pytest

import soundevent.io.crowsetta as crowsetta_io
from soundevent import data


@pytest.fixture
def bounding_box() -> data.BoundingBox:
    return data.BoundingBox(
        coordinates=[0.5, 0.5, 1.5, 1.5],
    )


@pytest.fixture
def sound_event(
    recording: data.Recording, bounding_box: data.BoundingBox
) -> data.SoundEvent:
    return data.SoundEvent(
        geometry=bounding_box,
        recording=recording,
        features=[data.Feature(name="test", value=1.0)],
    )


@pytest.fixture
def sound_event_annotation(
    user: data.User,
    sound_event: data.SoundEvent,
) -> data.SoundEventAnnotation:
    return data.SoundEventAnnotation(
        sound_event=sound_event,
        notes=[data.Note(message="random note", created_by=user)],
        tags=[
            data.Tag(key="animal", value="dog"),
        ],
    )


@pytest.fixture
def bbox() -> crowsetta.BBox:
    return crowsetta.BBox(
        onset=0.5,
        low_freq=0.5,
        high_freq=1.5,
        offset=1.5,
        label="dog",
    )


def test_bbox_from_annotation(
    sound_event_annotation: data.SoundEventAnnotation,
):
    bbox = crowsetta_io.bbox_from_annotation(sound_event_annotation)
    assert isinstance(bbox, crowsetta.BBox)
    assert bbox.onset == 0.5
    assert bbox.low_freq == 0.5
    assert bbox.high_freq == 1.5
    assert bbox.offset == 1.5
    assert bbox.label == "animal:dog"


def test_bbox_from_annotation_fails_on_other_geometries(
    sound_event_annotation: data.SoundEventAnnotation,
):
    sound_event_annotation.sound_event.geometry = data.LineString(
        coordinates=[[0.5, 0.5], [1.5, 1.5]],
    )

    with pytest.raises(ValueError):
        crowsetta_io.bbox_from_annotation(
            sound_event_annotation,
            cast_to_bbox=False,
        )


def test_bbox_from_annotation_fails_on_empty_geometry(
    recording: data.Recording,
):
    sound_event_annotation = data.SoundEventAnnotation(
        sound_event=data.SoundEvent(
            recording=recording,
            geometry=None,
        ),
    )

    with pytest.raises(ValueError):
        crowsetta_io.bbox_from_annotation(
            sound_event_annotation,
            cast_to_bbox=False,
        )


def test_bbox_from_annotations_can_cast_to_bbox(
    sound_event_annotation: data.SoundEventAnnotation,
):
    sound_event_annotation.sound_event.geometry = data.LineString(
        coordinates=[[0.5, 0.5], [1.5, 1.5]],
    )

    bbox = crowsetta_io.bbox_from_annotation(
        sound_event_annotation,
        cast_to_bbox=True,
    )
    assert isinstance(bbox, crowsetta.BBox)
    assert bbox.onset == 0.5
    assert bbox.low_freq == 0.5
    assert bbox.high_freq == 1.5
    assert bbox.offset == 1.5
    assert bbox.label == "animal:dog"


def test_bbox_from_annotation_fails_on_time_geometries(
    sound_event_annotation: data.SoundEventAnnotation,
):
    sound_event_annotation.sound_event.geometry = data.TimeInterval(
        coordinates=[0.5, 1.5],
    )

    with pytest.raises(ValueError):
        crowsetta_io.bbox_from_annotation(
            sound_event_annotation,
            cast_to_bbox=True,
        )


def test_bbox_from_annotation_cast_time_geometries(
    sound_event_annotation: data.SoundEventAnnotation,
):
    sound_event_annotation.sound_event.geometry = data.TimeInterval(
        coordinates=[0.5, 1.5],
    )

    bbox = crowsetta_io.bbox_from_annotation(
        sound_event_annotation,
        cast_to_bbox=True,
        raise_on_time_geometries=False,
    )
    nyquist = sound_event_annotation.sound_event.recording.samplerate / 2
    assert isinstance(bbox, crowsetta.BBox)
    assert bbox.onset == 0.5
    assert bbox.low_freq == 0
    assert bbox.high_freq == nyquist
    assert bbox.offset == 1.5
    assert bbox.label == "animal:dog"


def test_bbox_to_annotation(
    bbox: crowsetta.BBox,
    recording: data.Recording,
):
    annotation = crowsetta_io.bbox_to_annotation(bbox, recording)
    assert isinstance(annotation, data.SoundEventAnnotation)
    geometry = annotation.sound_event.geometry
    assert isinstance(geometry, data.BoundingBox)
    assert geometry.coordinates == [0.5, 0.5, 1.5, 1.5]
    assert annotation.tags == [data.Tag(key="crowsetta", value="dog")]


def test_bbox_to_annotation_with_notes_and_created_by(
    bbox: crowsetta.BBox,
    recording: data.Recording,
    user: data.User,
):
    note = data.Note(
        message="random note",
        created_by=user,
    )
    annotation = crowsetta_io.bbox_to_annotation(
        bbox, recording, notes=[note], created_by=user
    )
    assert annotation.notes == [note]
    assert annotation.created_by == user


def test_bbox_to_annotation_with_time_expanded_recording(
    bbox: crowsetta.BBox,
    time_expanded_recording: data.Recording,
):
    annotation = crowsetta_io.bbox_to_annotation(bbox, time_expanded_recording)
    assert annotation.sound_event.recording == time_expanded_recording
    geometry = annotation.sound_event.geometry
    assert isinstance(geometry, data.BoundingBox)
    assert tuple(geometry.coordinates) == (0.05, 5.0, 0.15, 15.0)


def test_bbox_to_annotation_with_time_expanded_recording_no_adjustment(
    bbox: crowsetta.BBox,
    time_expanded_recording: data.Recording,
):
    annotation = crowsetta_io.bbox_to_annotation(
        bbox,
        time_expanded_recording,
        adjust_time_expansion=False,
    )
    assert annotation.sound_event.recording == time_expanded_recording
    geometry = annotation.sound_event.geometry
    assert isinstance(geometry, data.BoundingBox)
    assert tuple(geometry.coordinates) == (0.5, 0.5, 1.5, 1.5)
