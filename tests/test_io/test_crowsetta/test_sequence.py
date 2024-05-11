"""Test suite for the soundevent.io.crowsetta.sequence module."""

from typing import List

import crowsetta
import numpy as np
import pytest

import soundevent.io.crowsetta as crowsetta_io
from soundevent import data
from soundevent.io.crowsetta.segment import create_crowsetta_segment


@pytest.fixture
def intervals() -> List[data.TimeInterval]:
    return [
        data.TimeInterval(coordinates=[0.5, 1.5]),
        data.TimeInterval(coordinates=[2.0, 2.5]),
    ]


@pytest.fixture
def sound_events(
    recording: data.Recording,
    intervals: List[data.TimeInterval],
) -> List[data.SoundEvent]:
    return [
        data.SoundEvent(
            geometry=interval,
            recording=recording,
            features=[data.Feature(name="test", value=1.0)],
        )
        for interval in intervals
    ]


@pytest.fixture
def sound_event_annotations(
    user: data.User,
    sound_events: List[data.SoundEvent],
) -> List[data.SoundEventAnnotation]:
    tags = [
        data.Tag(key="animal", value="dog"),
        data.Tag(key="animal", value="cat"),
    ]
    return [
        data.SoundEventAnnotation(
            sound_event=sound_event,
            notes=[data.Note(message="random note", created_by=user)],
            tags=[tag],
        )
        for sound_event, tag in zip(sound_events, tags)
    ]


@pytest.fixture
def sequence() -> crowsetta.Sequence:
    return crowsetta.Sequence.from_segments(
        [
            create_crowsetta_segment(
                label="dog",
                onset_s=0.5,
                offset_s=1.5,
            ),
            create_crowsetta_segment(
                label="cat",
                onset_s=2.0,
                offset_s=2.5,
            ),
        ],
    )


def test_sequence_from_annotations(
    sound_event_annotations: List[data.SoundEventAnnotation],
):
    sequence = crowsetta_io.sequence_from_annotations(sound_event_annotations)
    assert isinstance(sequence, crowsetta.Sequence)
    assert (sequence.onsets_s == np.array([0.5, 2.0])).all()
    assert (sequence.offsets_s == np.array([1.5, 2.5])).all()
    assert (sequence.labels == np.array(["animal:dog", "animal:cat"])).all()


def test_sequence_from_annotations_fails_on_non_compatible_geometries(
    recording: data.Recording,
):
    sound_event_annotations = [
        data.SoundEventAnnotation(
            sound_event=data.SoundEvent(
                recording=recording,
                geometry=data.LineString(coordinates=[[0.5, 0.5], [1.5, 1.5]]),
            ),
        ),
        data.SoundEventAnnotation(
            sound_event=data.SoundEvent(
                recording=recording,
                geometry=data.TimeInterval(coordinates=[0.5, 1.5]),
            ),
        ),
    ]

    with pytest.raises(ValueError):
        crowsetta_io.sequence_from_annotations(
            sound_event_annotations,
            cast_to_segment=False,
        )


def test_sequence_from_annotations_ignores_non_compatible_geometries(
    recording: data.Recording,
):
    sound_event_annotations = [
        data.SoundEventAnnotation(
            sound_event=data.SoundEvent(
                recording=recording,
                geometry=data.LineString(coordinates=[[0.5, 0.5], [1.5, 1.5]]),
            ),
        ),
        data.SoundEventAnnotation(
            sound_event=data.SoundEvent(
                recording=recording,
                geometry=data.TimeInterval(coordinates=[0.5, 1.5]),
            ),
        ),
    ]

    sequence = crowsetta_io.sequence_from_annotations(
        sound_event_annotations,
        cast_to_segment=False,
        ignore_errors=True,
    )
    assert isinstance(sequence, crowsetta.Sequence)
    assert len(sequence.segments) == 1


def test_sequence_from_annotation_casts_to_geometry(
    recording: data.Recording,
):
    sound_event_annotations = [
        data.SoundEventAnnotation(
            sound_event=data.SoundEvent(
                recording=recording,
                geometry=data.LineString(coordinates=[[0.5, 0.5], [1.5, 1.5]]),
            ),
        ),
        data.SoundEventAnnotation(
            sound_event=data.SoundEvent(
                recording=recording,
                geometry=data.TimeInterval(coordinates=[0.5, 1.5]),
            ),
        ),
    ]

    sequence = crowsetta_io.sequence_from_annotations(
        sound_event_annotations,
        cast_to_segment=True,
    )
    assert isinstance(sequence, crowsetta.Sequence)
    assert len(sequence.segments) == 2
    assert (sequence.onsets_s == np.array([0.5, 0.5])).all()
    assert (sequence.offsets_s == np.array([1.5, 1.5])).all()


def test_sequence_to_annotations(
    sequence: crowsetta.Sequence,
    recording: data.Recording,
):
    annotations = crowsetta_io.sequence_to_annotations(
        sequence,
        recording,
    )
    assert len(annotations) == 2
    assert all(
        isinstance(ann, data.SoundEventAnnotation) for ann in annotations
    )
    assert all(ann.sound_event.recording == recording for ann in annotations)
