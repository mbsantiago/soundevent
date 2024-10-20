import pytest

from soundevent import data
from soundevent.operations import segment_clip


def test_segment_clip_no_hop(recording: data.Recording):
    clip = data.Clip(
        start_time=0.0,
        end_time=10.0,
        recording=recording,
    )
    segments = list(segment_clip(clip, duration=2.0))
    assert [(s.start_time, s.end_time) for s in segments] == [
        (0, 2),
        (2, 4),
        (4, 6),
        (6, 8),
        (8, 10),
    ]


def test_segment_clip_with_hop(recording: data.Recording):
    clip = data.Clip(
        start_time=0.0,
        end_time=10.0,
        recording=recording,
    )
    segments = list(segment_clip(clip, duration=2.0, hop=1.0))
    assert [(s.start_time, s.end_time) for s in segments] == [
        (0, 2),
        (1, 3),
        (2, 4),
        (3, 5),
        (4, 6),
        (5, 7),
        (6, 8),
        (7, 9),
        (8, 10),
    ]


def test_segment_clip_include_incomplete(recording: data.Recording):
    clip = data.Clip(
        start_time=0.0,
        end_time=10.0,
        recording=recording,
    )
    segments = list(
        segment_clip(clip, duration=3.0, hop=2.0, include_incomplete=True)
    )
    assert [(s.start_time, s.end_time) for s in segments] == [
        (0, 3),
        (2, 5),
        (4, 7),
        (6, 9),
        (8, 10),
    ]


def test_segment_clip_exclude_incomplete(recording: data.Recording):
    clip = data.Clip(
        start_time=0.0,
        end_time=10.0,
        recording=recording,
    )
    segments = list(
        segment_clip(clip, duration=3.0, hop=2.0, include_incomplete=False)
    )
    assert [(s.start_time, s.end_time) for s in segments] == [
        (0, 3),
        (2, 5),
        (4, 7),
        (6, 9),
    ]


def test_segment_clip_invalid_input(recording: data.Recording):
    clip = data.Clip(
        start_time=0.0,
        end_time=10.0,
        recording=recording,
    )
    with pytest.raises(ValueError):
        list(segment_clip(clip, duration=0.0))
    with pytest.raises(ValueError):
        list(segment_clip(clip, duration=2.0, hop=-1.0))


def test_segment_clip_empty_clip(recording: data.Recording):
    clip = data.Clip(
        start_time=0.0,
        end_time=0.0,
        recording=recording,
    )
    segments = list(segment_clip(clip, duration=2.0))
    assert len(segments) == 0


def test_segment_clip_uuid_generation_is_deterministic(
    recording: data.Recording,
):
    clip = data.Clip(
        start_time=0.0,
        end_time=10.0,
        recording=recording,
    )
    segments1 = list(segment_clip(clip, duration=2.0, hop=1.0))
    segments2 = list(segment_clip(clip, duration=2.0, hop=1.0))

    for segment1, segment2 in zip(segments1, segments2):
        assert segment1.uuid == segment2.uuid
