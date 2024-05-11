"""Test suite for the soundevent.io.crowsetta.segments module."""

import crowsetta
import pytest

import soundevent.io.crowsetta as crowsetta_io
from soundevent import data
from soundevent.io.crowsetta.segment import (
    create_crowsetta_segment,
)


@pytest.fixture
def interval() -> data.TimeInterval:
    return data.TimeInterval(coordinates=[0.5, 1.5])


@pytest.fixture
def sound_event(
    recording: data.Recording, interval: data.TimeInterval
) -> data.SoundEvent:
    return data.SoundEvent(
        geometry=interval,
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
def segment() -> crowsetta.Segment:
    return create_crowsetta_segment(
        label="dog",
        onset_s=0.5,
        offset_s=1.5,
    )


def test_segment_from_annotation_fails_on_empty_geometry(
    recording: data.Recording,
):
    sound_event_annotation = data.SoundEventAnnotation(
        sound_event=data.SoundEvent(
            recording=recording,
            geometry=None,
        ),
    )

    with pytest.raises(ValueError):
        crowsetta_io.segment_from_annotation(sound_event_annotation)


def test_segment_to_annotation_without_onset_and_offset_in_seconds(
    recording: data.Recording,
):
    samplerate = recording.samplerate
    segment = create_crowsetta_segment(
        label="dog",
        onset_sample=3000,
        offset_sample=4000,
    )
    annotation = crowsetta_io.segment_to_annotation(segment, recording)
    assert isinstance(annotation, data.SoundEventAnnotation)
    geometry = annotation.sound_event.geometry
    assert isinstance(geometry, data.TimeInterval)
    assert tuple(geometry.coordinates) == (
        3000 / samplerate,
        4000 / samplerate,
    )


def test_segment_from_annotation(
    sound_event_annotation: data.SoundEventAnnotation,
):
    segment = crowsetta_io.segment_from_annotation(sound_event_annotation)
    assert isinstance(segment, crowsetta.Segment)
    assert segment.onset_s == 0.5
    assert segment.offset_s == 1.5
    assert segment.label == "animal:dog"


def test_segment_from_annotation_fails_if_not_a_time_interval(
    sound_event_annotation: data.SoundEventAnnotation,
):
    sound_event_annotation.sound_event.geometry = data.Point(
        coordinates=[0.5, 1]
    )
    with pytest.raises(ValueError):
        crowsetta_io.segment_from_annotation(
            sound_event_annotation,
            cast_to_segment=False,
        )


def test_segment_from_annotation_casts_to_segment(
    sound_event_annotation: data.SoundEventAnnotation,
):
    sound_event_annotation.sound_event.geometry = data.Point(
        coordinates=[0.5, 1]
    )
    segment = crowsetta_io.segment_from_annotation(
        sound_event_annotation,
        cast_to_segment=True,
    )
    assert isinstance(segment, crowsetta.Segment)
    assert segment.onset_s == 0.5
    assert segment.offset_s == 0.5
    assert segment.label == "animal:dog"


def test_segment_to_annotation(
    segment: crowsetta.Segment,
    recording: data.Recording,
):
    annotation = crowsetta_io.segment_to_annotation(segment, recording)
    assert isinstance(annotation, data.SoundEventAnnotation)
    geometry = annotation.sound_event.geometry
    assert isinstance(geometry, data.TimeInterval)
    assert tuple(geometry.coordinates) == (0.5, 1.5)
    assert annotation.sound_event.recording == recording
    assert annotation.tags == [data.Tag(key="crowsetta", value="dog")]


def test_segment_to_annotation_with_notes_and_created_by(
    segment: crowsetta.Segment,
    recording: data.Recording,
    user: data.User,
):
    note = data.Note(
        message="random note",
        created_by=user,
    )
    annotation = crowsetta_io.segment_to_annotation(
        segment,
        recording,
        created_by=user,
        notes=[note],
    )
    assert isinstance(annotation, data.SoundEventAnnotation)
    assert annotation.notes == [note]
    assert annotation.created_by == user


def test_segment_to_annotation_on_time_expanded_recording(
    segment: crowsetta.Segment,
    time_expanded_recording: data.Recording,
):
    annotation = crowsetta_io.segment_to_annotation(
        segment,
        time_expanded_recording,
    )
    assert isinstance(annotation, data.SoundEventAnnotation)
    geometry = annotation.sound_event.geometry
    assert isinstance(geometry, data.TimeInterval)
    assert tuple(geometry.coordinates) == (0.05, 0.15)


def test_segment_to_annotation_on_time_expanded_recording_without_adjustment(
    segment: crowsetta.Segment,
    time_expanded_recording: data.Recording,
):
    annotation = crowsetta_io.segment_to_annotation(
        segment,
        time_expanded_recording,
        adjust_time_expansion=False,
    )
    assert isinstance(annotation, data.SoundEventAnnotation)
    geometry = annotation.sound_event.geometry
    assert isinstance(geometry, data.TimeInterval)
    assert tuple(geometry.coordinates) == (0.5, 1.5)
